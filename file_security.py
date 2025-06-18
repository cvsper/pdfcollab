import os
import mimetypes
import hashlib
from werkzeug.utils import secure_filename
from PIL import Image
import magic
import uuid
from typing import Optional, Tuple, Dict, Any

class FileSecurityManager:
    def __init__(self, upload_folder: str = "uploads", max_file_size: int = 16 * 1024 * 1024):
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size
        
        # Allowed file types with their MIME types
        self.allowed_extensions = {
            'pdf': ['application/pdf'],
            'png': ['image/png'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'gif': ['image/gif'],
            'txt': ['text/plain'],
            'doc': ['application/msword'],
            'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        }
        
        # Dangerous file extensions to always reject
        self.dangerous_extensions = {
            'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
            'php', 'asp', 'aspx', 'jsp', 'py', 'rb', 'pl', 'sh', 'ps1'
        }
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def validate_file(self, file) -> Tuple[bool, str]:
        """Validate uploaded file for security and type compliance"""
        
        # Check if file is provided
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file size
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > self.max_file_size:
                return False, f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
        
        # Get original filename and extension
        filename = file.filename.lower()
        if '.' not in filename:
            return False, "File must have an extension"
        
        extension = filename.rsplit('.', 1)[1]
        
        # Check for dangerous extensions
        if extension in self.dangerous_extensions:
            return False, f"File type '{extension}' is not allowed for security reasons"
        
        # Check if extension is allowed
        if extension not in self.allowed_extensions:
            return False, f"File type '{extension}' is not supported"
        
        # Validate MIME type if possible
        try:
            # Read first chunk to check MIME type
            file.seek(0)
            file_data = file.read(2048)
            file.seek(0)  # Reset file pointer
            
            # Use python-magic to detect file type
            detected_mime = magic.from_buffer(file_data, mime=True)
            
            # Check if detected MIME type matches allowed types for this extension
            allowed_mimes = self.allowed_extensions[extension]
            if detected_mime not in allowed_mimes:
                return False, f"File content doesn't match extension. Expected: {allowed_mimes}, Got: {detected_mime}"
            
        except Exception as e:
            # If MIME detection fails, log but don't reject
            print(f"Warning: Could not detect MIME type: {e}")
        
        return True, "File validation passed"
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Use werkzeug's secure_filename
        safe_filename = secure_filename(filename)
        
        # Add timestamp and random component to prevent conflicts
        name, ext = os.path.splitext(safe_filename)
        timestamp = str(int(os.path.getctime('.') * 1000))[-8:]  # Last 8 digits
        random_part = uuid.uuid4().hex[:8]
        
        sanitized = f"{name}_{timestamp}_{random_part}{ext}"
        
        # Ensure filename isn't too long (filesystem limits)
        if len(sanitized) > 255:
            # Truncate name part but keep extension
            max_name_length = 255 - len(ext) - len(timestamp) - len(random_part) - 2
            name = name[:max_name_length]
            sanitized = f"{name}_{timestamp}_{random_part}{ext}"
        
        return sanitized
    
    def save_file_securely(self, file, document_id: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Save file with security validation and return file info"""
        
        # Validate file first
        is_valid, message = self.validate_file(file)
        if not is_valid:
            return False, message, {}
        
        try:
            # Generate secure filename
            original_filename = file.filename
            sanitized_filename = self.sanitize_filename(original_filename)
            
            # Add document ID prefix if provided
            if document_id:
                sanitized_filename = f"{document_id}_{sanitized_filename}"
            
            # Create full file path
            file_path = os.path.join(self.upload_folder, sanitized_filename)
            
            # Ensure the file doesn't already exist (should be rare with timestamp+random)
            counter = 1
            base_path = file_path
            while os.path.exists(file_path):
                name, ext = os.path.splitext(base_path)
                file_path = f"{name}_copy{counter}{ext}"
                counter += 1
            
            # Save the file
            file.save(file_path)
            
            # Calculate file hash for integrity checking
            file_hash = self.calculate_file_hash(file_path)
            
            # Get file info
            file_info = {
                'original_filename': original_filename,
                'saved_filename': os.path.basename(file_path),
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_hash': file_hash,
                'mime_type': self.get_mime_type(file_path)
            }
            
            return True, "File saved successfully", file_info
            
        except Exception as e:
            return False, f"Error saving file: {str(e)}", {}
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return ""
    
    def get_mime_type(self, file_path: str) -> str:
        """Get MIME type of saved file"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Fallback to magic detection
                mime_type = magic.from_file(file_path, mime=True)
            return mime_type or "application/octet-stream"
        except Exception as e:
            print(f"Error detecting MIME type: {e}")
            return "application/octet-stream"
    
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """Verify file integrity using hash comparison"""
        if not expected_hash:
            return True  # Can't verify if no hash provided
        
        current_hash = self.calculate_file_hash(file_path)
        return current_hash == expected_hash
    
    def delete_file_securely(self, file_path: str) -> bool:
        """Securely delete a file"""
        try:
            if os.path.exists(file_path):
                # Verify the file is in our upload directory (security check)
                abs_upload_path = os.path.abspath(self.upload_folder)
                abs_file_path = os.path.abspath(file_path)
                
                if not abs_file_path.startswith(abs_upload_path):
                    print(f"Security warning: Attempted to delete file outside upload directory: {file_path}")
                    return False
                
                # Delete the file
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def scan_for_malicious_content(self, file_path: str) -> Tuple[bool, str]:
        """Basic scan for potentially malicious content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check for common malicious patterns
            malicious_patterns = [
                b'<script',
                b'javascript:',
                b'eval(',
                b'exec(',
                b'system(',
                b'shell_exec',
                b'passthru',
                b'%PDF-\x00\x00',  # Malformed PDF header
            ]
            
            for pattern in malicious_patterns:
                if pattern in content.lower():
                    return False, f"Potentially malicious content detected: {pattern.decode('utf-8', errors='ignore')}"
            
            return True, "File appears clean"
            
        except Exception as e:
            return False, f"Error scanning file: {e}"
    
    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """Clean up files older than specified days"""
        import time
        
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        try:
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    
                    if file_age > max_age_seconds:
                        if self.delete_file_securely(file_path):
                            deleted_count += 1
                            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        return deleted_count
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive file information"""
        if not os.path.exists(file_path):
            return None
        
        try:
            stat_info = os.stat(file_path)
            
            return {
                'filename': os.path.basename(file_path),
                'file_path': file_path,
                'file_size': stat_info.st_size,
                'created_time': stat_info.st_ctime,
                'modified_time': stat_info.st_mtime,
                'mime_type': self.get_mime_type(file_path),
                'file_hash': self.calculate_file_hash(file_path)
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None