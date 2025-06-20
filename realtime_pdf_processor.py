#!/usr/bin/env python3
"""
Real-time PDF Processor for accurate field detection and position extraction
"""

import fitz  # PyMuPDF
import json
import os
import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

class RealtimePDFProcessor:
    """Enhanced PDF processor for real-time editing with accurate field detection"""
    
    def __init__(self):
        self.supported_field_types = {
            '/Tx': 'text',
            '/Btn': 'checkbox',
            '/Ch': 'select',
            '/Sig': 'signature'
        }
    
    def extract_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Extract comprehensive PDF information including dimensions and metadata"""
        try:
            doc = fitz.open(pdf_path)
            
            pdf_info = {
                'page_count': len(doc),
                'pages': [],
                'metadata': doc.metadata,
                'file_size': os.path.getsize(pdf_path),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Extract page information
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_info = {
                    'page_number': page_num + 1,
                    'width': page.rect.width,
                    'height': page.rect.height,
                    'rotation': page.rotation,
                    'media_box': {
                        'x0': page.rect.x0,
                        'y0': page.rect.y0,
                        'x1': page.rect.x1,
                        'y1': page.rect.y1
                    }
                }
                pdf_info['pages'].append(page_info)
            
            doc.close()
            return pdf_info
            
        except Exception as e:
            print(f"❌ Error extracting PDF info: {e}")
            return {'error': str(e)}
    
    def detect_fields_with_positions(self, pdf_path: str) -> Dict[str, Any]:
        """Detect all form fields with accurate positions and metadata"""
        try:
            doc = fitz.open(pdf_path)
            fields = []
            field_mapping = {}
            
            print(f"🔍 Analyzing PDF: {pdf_path}")
            print(f"📄 PDF has {len(doc)} pages")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_info = {
                    'width': page.rect.width,
                    'height': page.rect.height
                }
                
                # Extract form widgets
                widgets = list(page.widgets())
                print(f"📋 Page {page_num + 1}: Found {len(widgets)} form widgets")
                
                for widget_index, widget in enumerate(widgets):
                    field_info = self.extract_widget_info_detailed(
                        widget, page_num, widget_index, page_info
                    )
                    
                    if field_info:
                        fields.append(field_info)
                        field_mapping[field_info['pdf_field_name']] = field_info['id']
                        print(f"   ✅ {field_info['type'].upper()}: {field_info['name']}")
                
                # Detect text-based signature areas
                signature_areas = self.detect_signature_areas(page, page_num)
                for sig_area in signature_areas:
                    fields.append(sig_area)
                    field_mapping[sig_area['pdf_field_name']] = sig_area['id']
                    print(f"   ✍️  SIGNATURE AREA: {sig_area['name']}")
            
            doc.close()
            
            result = {
                'fields': fields,
                'field_mapping': field_mapping,
                'total_fields': len(fields),
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
            
            print(f"✅ Extracted {len(fields)} fields total")
            return result
            
        except Exception as e:
            print(f"❌ Error detecting fields: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def extract_widget_info_detailed(self, widget, page_num: int, widget_index: int, page_info: dict) -> Optional[Dict[str, Any]]:
        """Extract detailed widget information with accurate positioning"""
        try:
            # Get field name
            field_name = widget.field_name or f"field_{page_num + 1}_{widget_index + 1}"
            
            # Get field type
            widget_type = self.get_widget_type_detailed(widget)
            
            # Get position and dimensions
            rect = widget.rect
            position = {
                'x': rect.x0,
                'y': rect.y0,
                'width': rect.width,
                'height': rect.height,
                'page': page_num + 1,
                'page_width': page_info['width'],
                'page_height': page_info['height'],
                'relative_x': rect.x0 / page_info['width'] if page_info['width'] > 0 else 0,
                'relative_y': rect.y0 / page_info['height'] if page_info['height'] > 0 else 0,
                'relative_width': rect.width / page_info['width'] if page_info['width'] > 0 else 0,
                'relative_height': rect.height / page_info['height'] if page_info['height'] > 0 else 0
            }
            
            # Get field value and properties
            field_value = self.get_field_value(widget, widget_type)
            
            # Determine field assignment based on name/position
            assigned_to = self.determine_field_assignment(field_name, position)
            
            # Generate unique field ID
            field_id = str(uuid.uuid4())
            
            # Check if this should be treated as a signature field based on name
            if widget_type == 'text' and any(keyword in field_name.lower() for keyword in ['signature', 'sig']):
                widget_type = 'signature'
                print(f"   🖋️  Converting text field '{field_name}' to signature field")
            
            # Get styling information
            styling = self.extract_field_styling(widget)
            
            field_info = {
                'id': field_id,
                'name': self.generate_field_name(field_name, widget_type),
                'pdf_field_name': field_name,
                'type': widget_type,
                'value': field_value,
                'position': position,
                'styling': styling,
                'required': self.is_field_required(widget),
                'assigned_to': assigned_to,
                'widget_index': widget_index,
                'page': page_num + 1,
                'created_at': datetime.utcnow().isoformat(),
                'metadata': {
                    'field_flags': widget.field_flags if hasattr(widget, 'field_flags') else 0,
                    'field_type_code': widget.field_type if hasattr(widget, 'field_type') else 0,
                    'field_type_string': widget.field_type_string if hasattr(widget, 'field_type_string') else '',
                    'max_length': widget.text_maxlen if hasattr(widget, 'text_maxlen') else None
                }
            }
            
            return field_info
            
        except Exception as e:
            print(f"⚠️  Error processing widget {widget_index}: {e}")
            return None
    
    def get_widget_type_detailed(self, widget) -> str:
        """Determine widget type with enhanced detection"""
        try:
            field_type_code = widget.field_type
            field_type_string = getattr(widget, 'field_type_string', '')
            field_flags = getattr(widget, 'field_flags', 0)
            
            # Enhanced type detection
            if field_type_code == 1:  # PDF_WIDGET_TYPE_BUTTON
                if field_flags & 32768:  # Radio button flag
                    return 'radio'
                elif field_flags & 65536:  # Checkbox flag  
                    return 'checkbox'
                else:
                    return 'button'
            elif field_type_code == 2:  # PDF_WIDGET_TYPE_TEXT
                if field_type_string == 'CheckBox':
                    return 'checkbox'
                else:
                    # Determine text field subtype based on name
                    field_name = widget.field_name.lower() if widget.field_name else ''
                    if 'email' in field_name:
                        return 'email'
                    elif 'phone' in field_name or 'tel' in field_name:
                        return 'tel'
                    elif 'date' in field_name:
                        return 'date'
                    elif 'sign' in field_name:
                        return 'signature'
                    else:
                        return 'text'
            elif field_type_code == 3:  # PDF_WIDGET_TYPE_LISTBOX
                return 'select'
            elif field_type_code == 4:  # PDF_WIDGET_TYPE_COMBOBOX
                return 'select'
            elif field_type_code == 5:  # PDF_WIDGET_TYPE_SIGNATURE
                if field_type_string == 'RadioButton':
                    return 'radio'
                else:
                    return 'signature'
            else:
                return 'text'
                
        except Exception as e:
            print(f"⚠️  Error determining widget type: {e}")
            return 'text'
    
    def get_field_value(self, widget, widget_type: str) -> str:
        """Extract current field value"""
        try:
            if hasattr(widget, 'field_value') and widget.field_value is not None:
                if widget_type in ['checkbox', 'radio']:
                    # For boolean fields, convert to string
                    return 'true' if widget.field_value else 'false'
                else:
                    return str(widget.field_value)
            return ''
        except Exception:
            return ''
    
    def extract_field_styling(self, widget) -> Dict[str, Any]:
        """Extract styling information from widget"""
        try:
            styling = {
                'font_size': 12,
                'font_family': 'Arial',
                'color': '#000000',
                'background_color': '#ffffff',
                'border_color': '#cccccc',
                'border_width': 1,
                'text_align': 'left'
            }
            
            # Try to extract actual styling if available
            if hasattr(widget, 'text_font'):
                styling['font_family'] = widget.text_font
            if hasattr(widget, 'text_fontsize'):
                styling['font_size'] = widget.text_fontsize
            if hasattr(widget, 'text_color'):
                styling['color'] = self.convert_color_to_hex(widget.text_color)
            if hasattr(widget, 'fill_color'):
                styling['background_color'] = self.convert_color_to_hex(widget.fill_color)
            if hasattr(widget, 'border_color'):
                styling['border_color'] = self.convert_color_to_hex(widget.border_color)
            
            return styling
            
        except Exception:
            # Return default styling if extraction fails
            return {
                'font_size': 12,
                'font_family': 'Arial',
                'color': '#000000',
                'background_color': '#ffffff',
                'border_color': '#cccccc',
                'border_width': 1,
                'text_align': 'left'
            }
    
    def convert_color_to_hex(self, color) -> str:
        """Convert PDF color to hex format"""
        try:
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)
                return f"#{r:02x}{g:02x}{b:02x}"
            return '#000000'
        except Exception:
            return '#000000'
    
    def is_field_required(self, widget) -> bool:
        """Determine if field is required"""
        try:
            # Check field flags for required flag
            if hasattr(widget, 'field_flags'):
                return bool(widget.field_flags & 2)  # Required flag
            return False
        except Exception:
            return False
    
    def determine_field_assignment(self, field_name: str, position: dict) -> str:
        """Determine which user should fill this field"""
        field_name_lower = field_name.lower()
        
        # Signature field assignment based on specific names
        if any(keyword in field_name_lower for keyword in ['signature']):
            # Applicant signature goes to user1, property owner/landlord goes to user2
            if any(keyword in field_name_lower for keyword in ['applicant', 'resident', 'tenant']):
                return 'user1'
            elif any(keyword in field_name_lower for keyword in ['owner', 'landlord', 'property', 'manager']):
                return 'user2'
            else:
                # Default signature assignment: first signature to user1, second to user2
                if 'signature3' in field_name_lower:  # First signature in homeworks.pdf
                    return 'user1'
                elif 'property_ower_sig3' in field_name_lower:  # Second signature
                    return 'user2'
                else:
                    return 'user2'  # Default to user2 for other signatures
        
        # Based on position (right side of page typically user2)
        if position['relative_x'] > 0.6:
            return 'user2'
        
        # Default to user1
        return 'user1'
    
    def generate_field_name(self, pdf_field_name: str, field_type: str) -> str:
        """Generate human-readable field name"""
        # Special handling for specific signature fields
        if field_type == 'signature':
            if pdf_field_name == 'signature3':
                return 'Applicant Signature'
            elif pdf_field_name == 'property_ower_sig3':
                return 'Property Owner Signature'
        
        # Clean up the PDF field name
        name = pdf_field_name.replace('_', ' ').replace('-', ' ')
        
        # Convert to title case
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Add type context if needed
        if field_type == 'signature' and 'signature' not in name.lower():
            name += ' Signature'
        elif field_type == 'date' and 'date' not in name.lower():
            name += ' Date'
        elif field_type == 'email' and 'email' not in name.lower():
            name += ' Email'
        
        return name
    
    def detect_signature_areas(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect potential signature areas based on text and lines"""
        signature_areas = []
        
        try:
            # Look for signature-related text
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").lower()
                            if any(keyword in text for keyword in ["signature", "sign here", "signed"]):
                                bbox = span.get("bbox", [0, 0, 0, 0])
                                
                                # Create signature field
                                field_id = str(uuid.uuid4())
                                signature_area = {
                                    'id': field_id,
                                    'name': f'Signature Area (Page {page_num + 1})',
                                    'pdf_field_name': f'signature_area_{page_num + 1}_{len(signature_areas) + 1}',
                                    'type': 'signature',
                                    'value': '',
                                    'position': {
                                        'x': bbox[0],
                                        'y': bbox[1] + 20,  # Place signature below text
                                        'width': max(200, bbox[2] - bbox[0]),
                                        'height': 30,
                                        'page': page_num + 1,
                                        'page_width': page.rect.width,
                                        'page_height': page.rect.height,
                                        'relative_x': bbox[0] / page.rect.width,
                                        'relative_y': (bbox[1] + 20) / page.rect.height,
                                        'relative_width': max(200, bbox[2] - bbox[0]) / page.rect.width,
                                        'relative_height': 30 / page.rect.height
                                    },
                                    'styling': {
                                        'font_size': 14,
                                        'font_family': 'Arial',
                                        'color': '#000080',
                                        'background_color': '#fffacd',
                                        'border_color': '#cccccc',
                                        'border_width': 1,
                                        'text_align': 'left'
                                    },
                                    'required': True,
                                    'assigned_to': 'user2',
                                    'page': page_num + 1,
                                    'created_at': datetime.utcnow().isoformat(),
                                    'metadata': {
                                        'detected_from': 'text_analysis',
                                        'trigger_text': text
                                    }
                                }
                                signature_areas.append(signature_area)
        
        except Exception as e:
            print(f"⚠️  Error detecting signature areas: {e}")
        
        return signature_areas
    
    
    def generate_pdf_preview(self, pdf_path: str, page_num: int = 1, scale: float = 1.0) -> Optional[str]:
        """Generate base64 encoded preview image of PDF page"""
        try:
            doc = fitz.open(pdf_path)
            
            if page_num > len(doc):
                page_num = 1
            
            page = doc[page_num - 1]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            doc.close()
            return img_base64
            
        except Exception as e:
            print(f"❌ Error generating preview: {e}")
            return None
    
    def fill_pdf_realtime(self, pdf_path: str, field_values: Dict[str, Any], output_path: str) -> bool:
        """Fill PDF with real-time field values and generate output"""
        try:
            print(f"🎯 Real-time PDF filling: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            filled_count = 0
            
            # Create field mapping from values
            field_mapping = {}
            for field_id, field_data in field_values.items():
                if field_data.get('value') and field_data.get('pdf_field_name'):
                    field_mapping[field_data['pdf_field_name']] = field_data['value']
            
            print(f"📋 Processing {len(field_mapping)} field values")
            
            # Fill form fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name and field_name in field_mapping:
                        try:
                            value = field_mapping[field_name]
                            widget_type = self.get_widget_type_detailed(widget)
                            
                            if widget_type in ['checkbox', 'radio']:
                                widget.field_value = value.lower() in ['true', '1', 'yes', 'on']
                            elif widget_type == 'signature':
                                # For signature fields, clear form field and add cursive text overlay
                                widget.field_value = ""  # Clear form field
                                widget.update()
                                
                                # Add cursive signature overlay
                                rect = widget.rect
                                signature_x = rect.x0 + 3
                                signature_y = rect.y0 + rect.height - 3
                                signature_font_size = max(10, min(rect.height - 2, 14))
                                
                                try:
                                    # Try Times Roman Italic (most commonly available cursive-like font)
                                    page.insert_text(
                                        (signature_x, signature_y),
                                        str(value),
                                        fontsize=signature_font_size,
                                        color=(0, 0, 0.8),  # Dark blue for signatures
                                        fontname="tiri"  # Times Roman Italic
                                    )
                                    print(f"✅ Added cursive signature '{value}' for '{field_name}' (Times Italic)")
                                except Exception as font_error:
                                    # Fallback to Helvetica Italic
                                    try:
                                        page.insert_text(
                                            (signature_x, signature_y),
                                            str(value),
                                            fontsize=signature_font_size,
                                            color=(0, 0, 0.8),
                                            fontname="heli"  # Helvetica Italic
                                        )
                                        print(f"✅ Added cursive signature '{value}' for '{field_name}' (Helvetica Italic)")
                                    except Exception as fallback_error:
                                        # Try Courier Italic as final cursive attempt
                                        try:
                                            page.insert_text(
                                                (signature_x, signature_y),
                                                str(value),
                                                fontsize=signature_font_size,
                                                color=(0, 0, 0.8),
                                                fontname="coi"  # Courier Italic
                                            )
                                            print(f"✅ Added cursive signature '{value}' for '{field_name}' (Courier Italic)")
                                        except Exception as final_error:
                                            # Final fallback to regular font
                                            page.insert_text(
                                                (signature_x, signature_y),
                                                str(value),
                                                fontsize=signature_font_size,
                                                color=(0, 0, 0.8)
                                            )
                                            print(f"✅ Added signature '{value}' for '{field_name}' (regular font)")
                            else:
                                widget.field_value = str(value)
                            
                            if widget_type != 'signature':  # Signature already updated above
                                widget.update()
                            filled_count += 1
                            
                            if widget_type != 'signature':
                                print(f"✅ Filled {widget_type} field '{field_name}' with '{value}'")
                            
                        except Exception as e:
                            print(f"⚠️  Could not fill field '{field_name}': {e}")
            
            # All fields are now filled directly in form fields - no text overlays needed
            print(f"📋 All fields filled directly in PDF form fields (no overlay duplicates)")
            
            # Save filled PDF
            doc.save(output_path)
            doc.close()
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Real-time PDF created: {output_path} ({file_size:,} bytes)")
            print(f"📊 Successfully filled {filled_count} fields")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in real-time PDF filling: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_field_data(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize field data"""
        try:
            # Required fields
            required_fields = ['id', 'name', 'type', 'position']
            for field in required_fields:
                if field not in field_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate field type
            valid_types = ['text', 'email', 'tel', 'date', 'checkbox', 'radio', 'select', 'signature']
            if field_data['type'] not in valid_types:
                field_data['type'] = 'text'
            
            # Validate position
            position = field_data['position']
            required_pos_fields = ['x', 'y', 'width', 'height', 'page']
            for field in required_pos_fields:
                if field not in position:
                    raise ValueError(f"Missing position field: {field}")
            
            # Sanitize values
            if 'value' in field_data and field_data['value']:
                field_data['value'] = str(field_data['value']).strip()
            
            # Ensure styling exists
            if 'styling' not in field_data:
                field_data['styling'] = {
                    'font_size': 12,
                    'font_family': 'Arial',
                    'color': '#000000'
                }
            
            return field_data
            
        except Exception as e:
            raise ValueError(f"Invalid field data: {e}")

# Global instance
realtime_pdf_processor = RealtimePDFProcessor()

def get_realtime_pdf_processor() -> RealtimePDFProcessor:
    """Get the global real-time PDF processor instance"""
    return realtime_pdf_processor