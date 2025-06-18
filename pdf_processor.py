import fitz  # PyMuPDF
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import base64
from io import BytesIO
import uuid

class PDFProcessor:
    def __init__(self):
        self.supported_field_types = {
            '/Tx': 'text',
            '/Btn': 'checkbox', 
            '/Ch': 'select',
            '/Sig': 'signature'
        }
    
    def extract_fields_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """Enhanced PDF field extraction using PyMuPDF for better accuracy"""
        try:
            if not os.path.exists(pdf_path):
                return {"error": f"PDF file not found: {pdf_path}"}
            
            doc = fitz.open(pdf_path)
            fields = []
            
            print(f"🔍 Analyzing PDF with PyMuPDF: {pdf_path}")
            print(f"📄 PDF has {len(doc)} pages")
            
            total_widgets = 0
            total_annotations = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get page text for context analysis
                page_text_dict = page.get_text("dict")
                
                # Method 1: Extract form fields (widgets) from the page
                widgets = list(page.widgets())  # Convert generator to list
                total_widgets += len(widgets)
                
                print(f"📋 Page {page_num + 1}: Found {len(widgets)} form widgets")
                
                for i, widget in enumerate(widgets):
                    field_info = self.extract_widget_info_enhanced(widget, page_num, i, page_text_dict)
                    if field_info:
                        fields.append(field_info)
                        print(f"   ✅ Widget: {field_info['name']} ({field_info['type']}) at ({field_info['position']['x']:.1f}, {field_info['position']['y']:.1f})")
                
                # Method 2: Extract text annotations that might be fillable
                annotations = list(page.annots())  # Convert generator to list
                for annot in annotations:
                    if annot.type[1] in ['FreeText', 'Text', 'Square', 'Circle']:
                        field_info = self.extract_annotation_info(annot, page_num)
                        if field_info:
                            fields.append(field_info)
                            total_annotations += 1
                            print(f"   📝 Annotation: {field_info['name']} at ({field_info['position']['x']:.1f}, {field_info['position']['y']:.1f})")
                
                # Method 3: Try to detect potential form areas by text analysis
                text_fields = self.detect_text_based_fields(page, page_num)
                for field_info in text_fields:
                    fields.append(field_info)
                    print(f"   🔍 Text-based: {field_info['name']} at ({field_info['position']['x']:.1f}, {field_info['position']['y']:.1f})")
            
            print(f"📊 Summary: {total_widgets} widgets, {total_annotations} annotations, {len(fields)} total fields")
            
            # If still no form fields found, create intelligent defaults based on document analysis
            if not fields:
                print("📝 No form fields detected, creating intelligent defaults based on document content...")
                fields = self.create_intelligent_fields(doc)
            
            doc.close()
            
            print(f"✅ Total fields extracted: {len(fields)}")
            return {"fields": fields}
            
        except Exception as e:
            print(f"❌ Error in PyMuPDF extraction: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to process PDF with PyMuPDF: {str(e)}"}
    
    def extract_widget_info(self, widget, page_num: int, widget_index: int = 0) -> Optional[Dict[str, Any]]:
        """Extract information from a PDF widget (form field)"""
        try:
            # Get field name - try multiple approaches to get the real name
            field_name = None
            
            # Method 1: Direct field name
            if hasattr(widget, 'field_name') and widget.field_name:
                field_name = widget.field_name
            
            # Method 2: Try to get name from field label or nearby text
            if not field_name:
                field_name = self.extract_field_name_from_context(widget, page_num)
            
            # Method 3: Use field type and position as fallback
            if not field_name:
                field_name = f"{widget.field_type_string.replace('/', '').lower()}_{page_num}_{widget_index}"
            
            # Clean field name
            field_name = str(field_name).strip()
            
            # Get field type from widget
            field_type_code = widget.field_type
            field_type_string = widget.field_type_string
            
            print(f"   🔧 Widget details: name='{field_name}', type_code={field_type_code}, type_string='{field_type_string}'")
            
            # Map field type more accurately based on PyMuPDF field types
            if field_type_code == 1:  # PDF_WIDGET_TYPE_BUTTON
                if widget.field_flags & 32768:  # Radio button
                    field_type = 'radio'
                elif widget.field_flags & 65536:  # Checkbox
                    field_type = 'checkbox'
                else:
                    field_type = 'button'
            elif field_type_code == 2:  # PDF_WIDGET_TYPE_TEXT or CheckBox in some cases
                if field_type_string == 'CheckBox':
                    field_type = 'checkbox'
                else:
                    field_type = 'text'
            elif field_type_code == 3:  # PDF_WIDGET_TYPE_LISTBOX
                field_type = 'select'
            elif field_type_code == 4:  # PDF_WIDGET_TYPE_COMBOBOX
                field_type = 'select'
            elif field_type_code == 5:  # PDF_WIDGET_TYPE_SIGNATURE or RadioButton
                if field_type_string == 'RadioButton':
                    field_type = 'radio'
                else:
                    field_type = 'signature'
            elif field_type_code == 7:  # Text field
                field_type = 'text'
            else:
                field_type = self.supported_field_types.get(field_type_string, 'text')
            
            # Get field value
            field_value = widget.field_value or ""
            
            # Get field position and dimensions
            rect = widget.rect
            
            # Get field options if it's a choice field
            field_options = []
            try:
                if hasattr(widget, 'choice_values') and widget.choice_values:
                    field_options = widget.choice_values
            except:
                pass
            
            # Determine user assignment based on field characteristics
            assigned_to = self.determine_field_assignment(field_name, field_type)
            
            # Create unique ID that includes original field name for mapping
            field_id = f"pdf_{field_name}_{uuid.uuid4().hex[:6]}"
            
            field_info = {
                'id': field_id,
                'name': field_name,
                'type': field_type,
                'value': field_value,
                'position': {
                    'x': float(rect.x0),
                    'y': float(rect.y0),
                    'width': float(rect.width),
                    'height': float(rect.height)
                },
                'assigned_to': assigned_to,
                'page': page_num,
                'source': 'pymupdf_widget',
                'pdf_field_name': field_name,  # Keep original name for PDF filling
                'is_required': (widget.field_flags & 2) != 0,  # Check required flag
                'is_readonly': (widget.field_flags & 1) != 0,   # Check readonly flag
                'options': field_options,
                'field_flags': widget.field_flags,
                'field_type_code': field_type_code
            }
            
            return field_info
            
        except Exception as e:
            print(f"⚠️  Error extracting widget info: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_widget_info_enhanced(self, widget, page_num: int, widget_index: int, page_text_dict: dict) -> Optional[Dict[str, Any]]:
        """Enhanced widget info extraction with context analysis"""
        try:
            # Get field name using multiple strategies
            field_name = None
            original_field_name = None
            
            # Method 1: Direct field name
            if hasattr(widget, 'field_name') and widget.field_name:
                original_field_name = widget.field_name
                field_name = self.convert_field_name_to_readable(widget.field_name)
                print(f"   🏷️  Found direct field name: '{original_field_name}' -> '{field_name}'")
            
            # Method 2: Analyze nearby text for label
            if not field_name:
                field_name = self.find_nearby_label(widget, page_text_dict)
                if field_name:
                    print(f"   🔍 Found nearby label: '{field_name}'")
            
            # Method 3: Use field type and position as fallback
            if not field_name:
                widget_type = widget.field_type_string.replace('/', '').lower() if widget.field_type_string else 'field'
                field_name = f"{widget_type}_{page_num}_{widget_index}"
                print(f"   📍 Using position-based name: '{field_name}'")
            
            # Clean field name
            field_name = str(field_name).strip()
            
            # Get the standard widget info but override the name
            widget_info = self.extract_widget_info(widget, page_num, widget_index)
            if widget_info:
                widget_info['name'] = field_name
                # Update ID to reflect the new name
                widget_info['id'] = f"pdf_{field_name}_{uuid.uuid4().hex[:6]}"
                widget_info['pdf_field_name'] = original_field_name or field_name  # Keep original for PDF filling
                widget_info['display_name'] = field_name  # Human-readable name for display
                
                # Check if this should be a signature field based on field name
                if self.is_signature_field(original_field_name or field_name, field_name):
                    widget_info['type'] = 'signature'
                    print(f"   🖋️  Detected signature field: {field_name}")
            
            return widget_info
            
        except Exception as e:
            print(f"⚠️  Error in enhanced widget extraction: {e}")
            return None
    
    def find_nearby_label(self, widget, page_text_dict: dict) -> Optional[str]:
        """Find text label near the widget position"""
        try:
            widget_rect = widget.rect
            widget_x, widget_y = widget_rect.x0, widget_rect.y0
            
            # Search for text within a reasonable distance of the widget
            search_distance = 100  # pixels
            
            best_label = None
            best_distance = float('inf')
            
            # Scan through text blocks
            for block in page_text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if not text or len(text) < 2:
                                continue
                            
                            # Get text position
                            text_bbox = span["bbox"]
                            text_x, text_y = text_bbox[0], text_bbox[1]
                            
                            # Calculate distance from widget
                            distance = ((text_x - widget_x) ** 2 + (text_y - widget_y) ** 2) ** 0.5
                            
                            # Check if text is close enough and looks like a label
                            if distance < search_distance and self.looks_like_label(text):
                                if distance < best_distance:
                                    best_distance = distance
                                    best_label = text
            
            if best_label:
                # Clean the label
                cleaned_label = best_label.replace(':', '').replace('*', '').strip()
                cleaned_label = cleaned_label.replace(' ', '_').replace('-', '_')
                return cleaned_label
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error finding nearby label: {e}")
            return None
    
    def looks_like_label(self, text: str) -> bool:
        """Check if text looks like a field label"""
        text = text.strip().lower()
        
        # Skip if too long or too short
        if len(text) < 2 or len(text) > 50:
            return False
        
        # Skip if it's mostly numbers
        if text.replace('.', '').replace(',', '').isdigit():
            return False
            
        # Skip if it looks like filled data (contains multiple words with capitals)
        original_text = text.strip()
        if ' ' in original_text and any(c.isupper() for c in original_text):
            # If it has spaces and capitals, it might be a filled value like "John Doe Employee"
            word_count = len(original_text.split())
            if word_count > 2:  # More than 2 words likely indicates a filled value
                return False
        
        # Skip common non-label words
        skip_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        if text in skip_words:
            return False
            
        # Skip if it looks like a person's name (has proper case and common name patterns)
        if ' ' in text and all(word.istitle() for word in text.split()):
            return False
        
        # Look for common label patterns
        label_patterns = [
            'name', 'email', 'phone', 'address', 'date', 'signature', 'title', 
            'department', 'position', 'employee', 'manager', 'supervisor',
            'notes', 'comments', 'approval', 'authorize'
        ]
        
        # Check if text contains any label pattern
        for pattern in label_patterns:
            if pattern in text:
                return True
        
        # Check if it ends with common label endings
        if text.endswith(':') or text.endswith('*') or text.endswith('_'):
            return True
        
        # If it's a reasonable length and contains letters, consider it a potential label
        if 3 <= len(text) <= 30 and any(c.isalpha() for c in text):
            return True
        
        return False
    
    def convert_field_name_to_readable(self, field_name: str) -> str:
        """Convert technical field names to human-readable labels"""
        if not field_name:
            return field_name
            
        # Create a mapping of common technical field names to readable labels
        name_mappings = {
            # Address fields
            'property_address1': 'Property Address',
            'address3': 'Address',
            'apt_num1': 'Apartment Number',
            'city1': 'City',
            'city3': 'City',
            'state1': 'State',
            'zip1': 'ZIP Code',
            
            # Personal information
            'first_name2': 'First Name',
            'last_name2': 'Last Name',
            'phone2': 'Phone Number',
            'phone3': 'Phone Number',
            'phone_num1': 'Phone Number',
            'email2': 'Email Address',
            'email3': 'Email Address',
            
            # Dates and signatures
            'date3': 'Date',
            'signature3': 'Signature',
            'date_property_mang3': 'Property Manager Date',
            'property_ower_sig3': 'Property Owner Signature',
            
            # Property/Landlord information
            'landlord_name3': 'Landlord Name',
            
            # Household information
            'people_in_household4': 'Number of People in Household',
            'people_in_household_overage4': 'Additional Household Members',
            'annual_income4': 'Annual Income',
            
            # Utility information
            'elec_acct_num2': 'Electric Account Number',
            'gas_acct_num2': 'Gas Account Number',
            'elect_acct_other_name2': 'Electric Account Holder Name',
            'gas_acct_other_name2': 'Gas Account Holder Name',
            
            # Programs and benefits
            'elec_discount4': 'Electric Discount Program',
            'low_income4': 'Low Income Program',
            'matching_payment_eversource4': 'Eversource Matching Payment',
            'bill_forgive4': 'Bill Forgiveness Program',
            'matching_pay_united4': 'United Matching Payment',
            'ebt4': 'EBT (Food Stamps)',
            'energy_award_letter4': 'Energy Award Letter',
            'section_eight4': 'Section 8 Housing',
            'multifam4': 'Multi-Family Housing',
            
            # Dwelling types
            'dwelling_single_fam1': 'Single Family Home',
            'dwelling_apt1': 'Apartment',
            'dwelling_condo1': 'Condominium',
            
            # Fuel and utility types
            'fuel_type_elec2': 'Electric Heat',
            'fuel_type_gas2': 'Gas Heat',
            'fuel_type_oil2': 'Oil Heat',
            'fuel_type_propane2': 'Propane Heat',
            'electric_eversource2': 'Eversource Electric',
            'electric_ui2': 'United Illuminating Electric',
            'gas_util_cng2': 'Connecticut Natural Gas',
            'gas_util_eversource2': 'Eversource Gas',
            'gas_util_scg2': 'Southern Connecticut Gas',
            
            # Account ownership
            'owner2': 'Property Owner',
            'renter2': 'Renter/Tenant',
            'elect_acct_applicant2': 'Electric Account - Applicant',
            'elect_acct_other2': 'Electric Account - Other Person',
            'gas_acct_applicant2': 'Gas Account - Applicant',
            'gas_acct_other2': 'Gas Account - Other Person',
            'elect_acct_other_acct2': 'Electric Account - Other Account',
        }
        
        # First check for exact match
        if field_name in name_mappings:
            return name_mappings[field_name]
        
        # If no exact match, try to create a readable name from the field name
        readable_name = field_name
        
        # Remove numbers and underscores, then title case
        readable_name = ''.join(char if char.isalpha() or char == '_' else ' ' for char in readable_name)
        readable_name = readable_name.replace('_', ' ').strip()
        
        # Handle common abbreviations and patterns
        word_replacements = {
            'acct': 'Account',
            'num': 'Number',
            'addr': 'Address',
            'mgr': 'Manager',
            'sig': 'Signature',
            'util': 'Utility',
            'elec': 'Electric',
            'dept': 'Department',
            'emp': 'Employee',
            'tel': 'Telephone',
            'apt': 'Apartment',
            'st': 'Street',
            'ln': 'Lane',
            'rd': 'Road',
            'ave': 'Avenue',
            'blvd': 'Boulevard',
        }
        
        words = readable_name.split()
        for i, word in enumerate(words):
            if word.lower() in word_replacements:
                words[i] = word_replacements[word.lower()]
        
        readable_name = ' '.join(words)
        
        # Title case the result
        readable_name = readable_name.title()
        
        # Clean up any remaining issues
        readable_name = ' '.join(readable_name.split())  # Remove extra spaces
        
        return readable_name if readable_name else field_name
    
    def is_signature_field(self, pdf_field_name: str, display_name: str) -> bool:
        """Check if a field should be treated as a signature field"""
        # Combine both field names for checking
        combined_text = f"{pdf_field_name} {display_name}".lower()
        
        # Common signature field indicators
        signature_keywords = [
            'signature', 'sign', 'signed', 'sig', 'autograph', 'signiture',
            'manager_signature', 'supervisor_signature', 'employee_signature',
            'property_owner_signature', 'landlord_signature', 'tenant_signature',
            'applicant_signature', 'applicant_sig', 'applicant_signiture'
        ]
        
        return any(keyword in combined_text for keyword in signature_keywords)
    
    def extract_annotation_info(self, annot, page_num: int) -> Optional[Dict[str, Any]]:
        """Extract information from text annotations"""
        try:
            content = annot.info.get("content", "")
            if not content or len(content.strip()) < 2:
                return None
            
            field_name = f"annotation_{content[:20].replace(' ', '_')}"
            rect = annot.rect
            
            field_info = {
                'id': f"annotation_{uuid.uuid4().hex[:8]}",
                'name': field_name,
                'type': 'text',
                'value': content,
                'position': {
                    'x': float(rect.x0),
                    'y': float(rect.y0),
                    'width': float(rect.width),
                    'height': float(rect.height)
                },
                'assigned_to': self.determine_field_assignment(field_name, 'text'),
                'page': page_num,
                'source': 'pymupdf_annotation'
            }
            
            return field_info
            
        except Exception as e:
            print(f"⚠️  Error extracting annotation info: {e}")
            return None
    
    def detect_text_based_fields(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect potential form fields by analyzing text patterns"""
        fields = []
        
        try:
            # Get text with positioning information
            text_dict = page.get_text("dict")
            
            # Common field patterns to look for
            field_patterns = [
                # Name fields
                (r'(?i)(name|nome|nom|nombre)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(first\s*name|given\s*name)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(last\s*name|family\s*name|surname)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(full\s*name|complete\s*name)[\s:_-]*$', 'text', 'user1'),
                
                # Contact fields
                (r'(?i)(email|e-mail|mail)[\s:_-]*$', 'email', 'user1'),
                (r'(?i)(phone|telephone|tel|mobile|cell)[\s:_-]*$', 'tel', 'user1'),
                (r'(?i)(address|addr)[\s:_-]*$', 'text', 'user1'),
                
                # Date fields
                (r'(?i)(date|fecha|datum)[\s:_-]*$', 'date', 'user1'),
                (r'(?i)(birth|born|birthday|dob)[\s:_-]*$', 'date', 'user1'),
                (r'(?i)(start\s*date|hire\s*date)[\s:_-]*$', 'date', 'user1'),
                
                # Employment fields
                (r'(?i)(employee|emp)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(department|dept)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(position|title|job)[\s:_-]*$', 'text', 'user1'),
                (r'(?i)(salary|wage|compensation)[\s:_-]*$', 'text', 'user1'),
                
                # Signature/approval fields
                (r'(?i)(signature|sign|signed)[\s:_-]*$', 'signature', 'user2'),
                (r'(?i)(manager|supervisor|boss)[\s:_-]*$', 'text', 'user2'),
                (r'(?i)(approve|approval|authorized)[\s:_-]*$', 'text', 'user2'),
                (r'(?i)(hr|human\s*resources)[\s:_-]*$', 'text', 'user2'),
            ]
            
            import re
            detected_fields = []
            
            # Scan through text blocks
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_bbox = None
                        
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                line_text += text + " "
                                if line_bbox is None:
                                    line_bbox = span["bbox"]
                        
                        line_text = line_text.strip()
                        
                        # Check against patterns
                        for pattern, field_type, assigned_to in field_patterns:
                            if re.search(pattern, line_text):
                                if line_bbox:
                                    field_name = re.sub(r'[\s:_-]+$', '', line_text)
                                    field_name = re.sub(r'^[\s:_-]+', '', field_name)
                                    
                                    if field_name and len(field_name) > 1:
                                        field_info = {
                                            'id': f"text_detect_{len(detected_fields)}_{uuid.uuid4().hex[:6]}",
                                            'name': field_name,
                                            'type': field_type,
                                            'value': '',
                                            'position': {
                                                'x': float(line_bbox[2] + 10),  # Position input field after label
                                                'y': float(line_bbox[1]),
                                                'width': 150.0,
                                                'height': 20.0
                                            },
                                            'assigned_to': assigned_to,
                                            'page': page_num,
                                            'source': 'text_detection',
                                            'confidence': 0.8
                                        }
                                        detected_fields.append(field_info)
                                        break  # Don't match multiple patterns for same text
            
            # Remove duplicates and overlapping fields
            unique_fields = []
            for field in detected_fields:
                is_duplicate = False
                for existing in unique_fields:
                    # Check if fields are too close (likely duplicates)
                    x_diff = abs(field['position']['x'] - existing['position']['x'])
                    y_diff = abs(field['position']['y'] - existing['position']['y'])
                    if x_diff < 50 and y_diff < 20:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_fields.append(field)
            
            return unique_fields
            
        except Exception as e:
            print(f"⚠️  Error in text-based field detection: {e}")
            return []
    
    def extract_field_name_from_context(self, widget, page_num: int) -> Optional[str]:
        """Extract field name from surrounding text context"""
        try:
            # Get the field position
            rect = widget.rect
            field_x, field_y = rect.x0, rect.y0
            
            # Open the document to analyze text near the field
            # Note: This is a simplified approach - in a real implementation,
            # you'd want to pass the document object or page object
            return None  # For now, return None to use fallback naming
            
        except Exception as e:
            print(f"⚠️  Error extracting field name from context: {e}")
            return None
    
    def create_intelligent_fields(self, doc) -> List[Dict[str, Any]]:
        """Create intelligent field suggestions based on document text analysis"""
        fields = []
        
        # Analyze document text to suggest common fields
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        
        text_lower = text_content.lower()
        
        # Common field patterns and their likely positions
        field_patterns = [
            # Personal Information
            {"keywords": ["name", "full name", "employee name"], "name": "Full Name", "type": "text", "assigned_to": "user1"},
            {"keywords": ["email", "e-mail", "email address"], "name": "Email Address", "type": "email", "assigned_to": "user1"},
            {"keywords": ["phone", "telephone", "contact"], "name": "Phone Number", "type": "tel", "assigned_to": "user1"},
            {"keywords": ["address", "street", "city"], "name": "Address", "type": "text", "assigned_to": "user1"},
            
            # Employment Information
            {"keywords": ["employee id", "emp id", "staff id"], "name": "Employee ID", "type": "text", "assigned_to": "user1"},
            {"keywords": ["department", "dept"], "name": "Department", "type": "text", "assigned_to": "user1"},
            {"keywords": ["position", "title", "job title"], "name": "Position/Title", "type": "text", "assigned_to": "user1"},
            {"keywords": ["start date", "hire date", "employment date"], "name": "Start Date", "type": "date", "assigned_to": "user1"},
            {"keywords": ["salary", "wage", "compensation"], "name": "Salary", "type": "text", "assigned_to": "user1"},
            
            # Approval/Management Information
            {"keywords": ["manager", "supervisor", "manager name"], "name": "Manager Name", "type": "text", "assigned_to": "user2"},
            {"keywords": ["signature", "sign", "manager signature"], "name": "Manager Signature", "type": "signature", "assigned_to": "user2"},
            {"keywords": ["approval", "approved", "hr approval"], "name": "HR Approval", "type": "text", "assigned_to": "user2"},
            {"keywords": ["date", "approval date", "signed date"], "name": "Approval Date", "type": "date", "assigned_to": "user2"},
            {"keywords": ["notes", "comments", "remarks"], "name": "Additional Notes", "type": "textarea", "assigned_to": "user2"},
        ]
        
        y_position = 700  # Start from top
        x_positions = [100, 350]  # Two columns
        
        for i, pattern in enumerate(field_patterns):
            # Check if any keywords are found in the document
            if any(keyword in text_lower for keyword in pattern["keywords"]):
                field_height = 60 if pattern["type"] == "textarea" else 30
                
                field = {
                    'id': f"intelligent_{i}",
                    'name': pattern["name"],
                    'type': pattern["type"],
                    'value': '',
                    'position': {
                        'x': x_positions[i % 2],
                        'y': y_position - (i // 2) * 50,
                        'width': 200,
                        'height': field_height
                    },
                    'assigned_to': pattern["assigned_to"],
                    'page': 0,
                    'source': 'intelligent_analysis',
                    'is_suggested': True
                }
                fields.append(field)
        
        return fields
    
    def determine_field_assignment(self, field_name: str, field_type: str) -> str:
        """Determine which user should fill this field based on name and type"""
        field_name_lower = field_name.lower()
        
        # User 2 (manager/supervisor) keywords
        user2_keywords = [
            'manager', 'supervisor', 'hr', 'human resources', 'boss', 'director', 
            'admin', 'authorize', 'approve', 'approval'
        ]
        
        # User 1 (employee/applicant) signature keywords
        user1_signature_keywords = [
            'property_owner', 'tenant', 'applicant', 'employee', 'landlord'
        ]
        
        # Check for user-specific signature fields
        if field_type == 'signature':
            # Check if it's specifically a user1 signature
            if any(keyword in field_name_lower for keyword in user1_signature_keywords):
                return 'user1'
            # Check if it's specifically a user2 signature  
            elif any(keyword in field_name_lower for keyword in user2_keywords):
                return 'user2'
            # Generic "signature" field goes to user2 (authority figure)
            elif 'signature' in field_name_lower and not any(keyword in field_name_lower for keyword in user1_signature_keywords):
                return 'user2'
        
        # Non-signature fields
        if any(keyword in field_name_lower for keyword in user2_keywords):
            return 'user2'
        
        return 'user1'
    
    def fill_pdf_with_pymupdf(self, pdf_path: str, document: Dict[str, Any], output_path: str) -> bool:
        """Fill PDF using PyMuPDF with signature support"""
        try:
            print(f"🎯 Filling PDF with PyMuPDF: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            filled_count = 0
            
            # Create field mapping from document
            field_mapping = {}
            signature_fields = {}
            
            if 'pdf_fields' in document:
                for field in document['pdf_fields']:
                    if field.get('value'):
                        field_key = field.get('pdf_field_name', field['name'])
                        field_mapping[field_key] = field['value']
                        
                        # Track signature fields separately
                        if field.get('type') == 'signature':
                            signature_fields[field_key] = {
                                'value': field['value'],
                                'position': field.get('position', {}),
                                'page': field.get('page', 0),
                                'name': field.get('name', '')
                            }
            
            print(f"📋 Created field mapping with {len(field_mapping)} entries")
            print(f"🖋️  Found {len(signature_fields)} signature fields")
            
            # Fill regular form fields first
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name and field_name in field_mapping:
                        # Skip signature fields - handle them separately
                        if field_name in signature_fields:
                            continue
                            
                        try:
                            field_value = field_mapping[field_name]
                            widget.field_value = str(field_value)
                            widget.update()
                            filled_count += 1
                            print(f"✅ Filled field '{field_name}' with '{field_value}'")
                        except Exception as e:
                            print(f"⚠️  Could not fill field '{field_name}': {e}")
            
            # Handle signature fields with image insertion
            for field_name, sig_data in signature_fields.items():
                try:
                    self.insert_signature_on_pdf(doc, field_name, sig_data)
                    filled_count += 1
                    print(f"🖋️  Inserted signature for field '{field_name}'")
                except Exception as e:
                    print(f"⚠️  Could not insert signature for '{field_name}': {e}")
            
            # Save the filled PDF
            doc.save(output_path)
            doc.close()
            
            print(f"✅ Successfully filled {filled_count} fields using PyMuPDF")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error filling PDF with PyMuPDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def insert_signature_on_pdf(self, doc, field_name: str, sig_data: dict):
        """Insert signature image onto PDF at the correct position"""
        try:
            page_num = sig_data.get('page', 0)
            position = sig_data.get('position', {})
            signature_value = sig_data.get('value', '')
            
            if page_num >= len(doc):
                print(f"⚠️  Invalid page number {page_num} for signature field")
                return
            
            page = doc[page_num]
            
            # Handle different signature value formats
            if signature_value.startswith('data:image/'):
                # Base64 image data
                self.insert_signature_image(page, signature_value, position, field_name)
            else:
                # Text signature - insert as styled text
                self.insert_signature_text(page, signature_value, position, field_name)
                
        except Exception as e:
            print(f"❌ Error inserting signature for {field_name}: {e}")
            raise
    
    def insert_signature_image(self, page, signature_data: str, position: dict, field_name: str):
        """Insert base64 signature image onto PDF page"""
        try:
            # Extract base64 data
            if ',' in signature_data:
                base64_data = signature_data.split(',')[1]
            else:
                base64_data = signature_data
            
            # Decode base64 to image
            import base64
            image_data = base64.b64decode(base64_data)
            
            # Create a temporary image file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            try:
                # Define signature area from position
                x = position.get('x', 0)
                y = position.get('y', 0)  
                width = position.get('width', 100)
                height = position.get('height', 30)
                
                # Convert PDF coordinates (y flipped)
                page_height = page.rect.height
                rect = fitz.Rect(x, page_height - y - height, x + width, page_height - y)
                
                # Insert image
                page.insert_image(rect, filename=temp_file_path)
                print(f"🖼️  Inserted signature image for '{field_name}' at ({x}, {y})")
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"❌ Error inserting signature image: {e}")
            raise
    
    def insert_signature_text(self, page, signature_text: str, position: dict, field_name: str):
        """Insert text signature with signature font styling"""
        try:
            x = position.get('x', 0)
            y = position.get('y', 0)
            width = position.get('width', 100)
            height = position.get('height', 30)
            
            # Use coordinates directly - PyMuPDF widget coordinates are already correct
            # Add small offsets for better visual placement within the field
            text_x = x + 2  # Small left margin
            text_y = y + (height * 0.7)  # Position text baseline properly within field
            
            print(f"🎯 Placing signature at field coordinates: x={x:.1f}, y={y:.1f}, size={width:.1f}x{height:.1f}")
            print(f"🎯 Adjusted text position: x={text_x:.1f}, y={text_y:.1f}")
            
            # Insert styled text to look like a signature
            # Use default font if italic not available
            try:
                page.insert_text(
                    (text_x, text_y),
                    signature_text,
                    fontsize=max(10, min(height - 2, 16)),  # Scale font to field height
                    color=(0, 0, 0.7),  # Dark blue color
                    fontname="helv-oblique"  # Italic font for signature look
                )
            except:
                # Fallback to default font
                page.insert_text(
                    (text_x, text_y),
                    signature_text,
                    fontsize=max(10, min(height - 2, 16)),  # Scale font to field height
                    color=(0, 0, 0.7)  # Dark blue color, no font specified (uses default)
                )
            
            print(f"✍️  Inserted signature text '{signature_text}' for '{field_name}' at field position ({x:.1f}, {y:.1f})")
            
        except Exception as e:
            print(f"❌ Error inserting signature text: {e}")
            raise
    
    def convert_pdf_to_image(self, pdf_path: str, page_num: int = None, dpi: int = 150) -> str:
        """Convert PDF page to image using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            
            # If no page specified, find the page with the most form fields
            if page_num is None:
                best_page = 0
                max_widgets = 0
                
                for p_num in range(len(doc)):
                    page = doc[p_num]
                    widgets = list(page.widgets())
                    if len(widgets) > max_widgets:
                        max_widgets = len(widgets)
                        best_page = p_num
                
                page_num = best_page
                print(f"🎯 Auto-selected page {page_num + 1} with {max_widgets} form fields for preview")
            
            if page_num >= len(doc):
                page_num = 0
            
            page = doc[page_num]
            
            # Render page to image
            mat = fitz.Matrix(dpi/72, dpi/72)  # Scaling matrix
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(BytesIO(img_data))
            
            # Save as base64 string for web display
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            doc.close()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"❌ Error converting PDF to image: {e}")
            return None
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get PDF information using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'has_forms': False,
                'form_field_count': 0,
                'pages': []
            }
            
            total_widgets = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())  # Convert generator to list
                widget_count = len(widgets)
                total_widgets += widget_count
                
                page_info = {
                    'page_number': page_num + 1,
                    'width': page.rect.width,
                    'height': page.rect.height,
                    'widget_count': widget_count,
                    'text_length': len(page.get_text())
                }
                info['pages'].append(page_info)
            
            info['has_forms'] = total_widgets > 0
            info['form_field_count'] = total_widgets
            
            doc.close()
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting PDF info: {e}")
            return {'error': str(e)}
    
    def create_overlay_pdf(self, original_pdf: str, field_data: List[Dict[str, Any]], output_path: str) -> bool:
        """Create a new PDF with text overlaid on the original"""
        try:
            print(f"🎨 Creating overlay PDF: {output_path}")
            
            doc = fitz.open(original_pdf)
            
            for field in field_data:
                if not field.get('value'):
                    continue
                
                page_num = field.get('page', 0)
                if page_num >= len(doc):
                    continue
                
                page = doc[page_num]
                position = field.get('position', {})
                
                # Create text annotation or insert text
                text_rect = fitz.Rect(
                    position.get('x', 0),
                    position.get('y', 0),
                    position.get('x', 0) + position.get('width', 100),
                    position.get('y', 0) + position.get('height', 20)
                )
                
                # Insert text at the specified position
                page.insert_text(
                    (position.get('x', 0), position.get('y', 0) + 12),  # Adjust y for baseline
                    field['value'],
                    fontsize=10,
                    color=(0, 0, 0),  # Black text
                    fontname="helv"   # Helvetica font
                )
                
                print(f"✅ Added overlay text '{field['value']}' at page {page_num}")
            
            doc.save(output_path)
            doc.close()
            
            print(f"✅ Successfully created overlay PDF")
            return True
            
        except Exception as e:
            print(f"❌ Error creating overlay PDF: {e}")
            import traceback
            traceback.print_exc()
            return False