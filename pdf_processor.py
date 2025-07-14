import fitz  # PyMuPDF
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import base64
from io import BytesIO
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

class PDFProcessor:
    def __init__(self):
        self.supported_field_types = {
            '/Tx': 'text',
            '/Btn': 'checkbox', 
            '/Ch': 'select',
            '/Sig': 'signature'
        }
        
        # Map from display names (with suffixes) to actual PDF field names
        self.field_type_map = {
            # Section 1: Property Information fields
            'Property Address': 'property_address1',
            'Apartment Number': 'apt_num1',
            'City': 'city1',
            'State': 'state1',
            'ZIP Code': 'zip1',
            'Number of Apartments': 'num_of_apt1',
            
            # Section 2: Personal info  
            'First Name': 'first_name2',
            'Last Name': 'last_name2',
            'Phone Number': 'phone2',
            'Email Address': 'email2',
            'Phone Number (Additional)': 'phone_num1',  # Additional phone field in Section 1
            'Telephone': 'phone_num1',  # Alternative name for additional phone field
            
            # Section 2: Dwelling type checkboxes
            'Single Family Home (Checkbox)': 'dwelling_single_fam1',
            'Apartment (Checkbox)': 'dwelling_apt1', 
            'Condominium (Checkbox)': 'dwelling_condo1',
            
            # Section 2: Heating fuel radio buttons
            'Electric Heat (Radio Button)': 'fuel_type_elec2',
            'Gas Heat (Radio Button)': 'fuel_type_gas2',
            'Oil Heat (Radio Button)': 'fuel_type_oil2',
            'Propane Heat (Radio Button)': 'fuel_type_propane2',
            
            # Section 2: Applicant type
            'Property Owner (Radio Button)': 'owner2',
            'Renter (Radio Button)': 'renter2',
            
            # Section 2: Electric utility options
            'Electric Eversource (Radio Button)': 'electric_eversource2',
            'Electric UI (Radio Button)': 'electric_ui2',
            
            # Section 2: Gas utility options  
            'Gas Util CNG (Radio Button)': 'gas_util_cng2',
            'Gas Util Eversource (Radio Button)': 'gas_util_eversource2',
            'Gas Util SCG (Radio Button)': 'gas_util_scg2',
            
            # Section 2: Account holder options
            'Electric Account Applicant (Radio Button)': 'elect_acct_applicant2',
            'Electric Account Other (Radio Button)': 'elect_acct_other2',
            'Gas Account Applicant (Radio Button)': 'gas_acct_applicant2',
            'Gas Account Other (Radio Button)': 'gas_acct_other2',
            'Electric Account Other Account (Radio Button)': 'elect_acct_other_acct2',
            
            # Section 2: Account names and numbers
            'Electric Account Other Name': 'elect_acct_other_name2',
            'Gas Account Other Name': 'gas_acct_other_name2',
            'Electric Account Number': 'elec_acct_num2',
            'Gas Account Number': 'gas_acct_num2',
            
            # Section 4: Owner/Landlord info
            'Landlord Name': 'landlord_name3',
            'Landlord Address': 'address3',
            'Landlord City': 'city3',
            'Landlord State': 'text_55cits',  # State field for landlord
            'Landlord ZIP': 'text_56qpfj',    # ZIP field for landlord
            'Landlord Phone': 'phone3',
            'Landlord Email': 'email3',
            
            # Property Owner info (frontend field names)
            'Property Owner Name': 'landlord_name3',
            'Property Owner Address': 'address3',
            'Property Owner City': 'city3',
            'Property Owner State': 'text_55cits',
            'Property Owner ZIP': 'text_56qpfj',
            'Property Owner Phone': 'phone3',
            'Property Owner Email': 'email3',
            
            # Section 4: Signatures
            'Applicant Signature': 'signature3',
            'Property Owner Signature': 'property_ower_sig3',
            
            # Date fields - map to specific widget names based on Y position
            'Date': 'date',  # Generic mapping for Date fields
            
            # Section 3: Qualification checkboxes (Option A)
            'Elec Discount4 (Checkbox)': 'elec_discount4',
            'Low Income Program (Checkbox)': 'low_income4',
            'Matching Payment Eversource4 (Checkbox)': 'matching_payment_eversource4',
            'Bill Forgiveness Program (Checkbox)': 'bill_forgive4',
            'Matching Pay United4 (Checkbox)': 'matching_pay_united4',
            
            # Section 3: Qualification checkboxes (Option B)
            'EBT (Food Stamps) (Checkbox)': 'ebt4',
            'Energy Award Letter4 (Checkbox)': 'energy_award_letter4',
            'Section Eight4 (Checkbox)': 'section_eight4',
            
            # Section 3: Qualification checkbox (Option D)
            'Multifam4 (Checkbox)': 'multifam4',
            
            # Section 3: Income information text fields
            'People In Household4': 'people_in_household4',
            'People In Household Overage4': 'people_in_household_overage4',
            'Annual Income4': 'annual_income4',
            
            # Additional field mappings for missing fields identified by test  
            # These are for disambiguating fields with duplicate display names
            'Phone Number (Additional)': 'phone_num1',    # Additional phone field at position (37,210)
            'City (Landlord)': 'city3',                   # Landlord city field at position (35,601)  
            'Phone Number (Landlord)': 'phone3',          # Landlord phone field at position (36,629)
            'Email Address (Landlord)': 'email3'          # Landlord email field at position (36,655)
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
            return {"success": True, "fields": fields}
            
        except Exception as e:
            print(f"❌ Error in PyMuPDF extraction: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to process PDF with PyMuPDF: {str(e)}"}
    
    def extract_widget_info_enhanced(self, widget, page_num: int, widget_index: int, page_text_dict: dict) -> Optional[Dict[str, Any]]:
        """Enhanced widget information extraction with better field type detection"""
        try:
            # Get field name - try multiple approaches to get the real name
            field_name = None
            
            # Method 1: Direct field name
            if hasattr(widget, 'field_name') and widget.field_name:
                field_name = widget.field_name
            
            # Method 2: Use field type and position as fallback
            if not field_name:
                field_type = self.get_widget_type(widget)
                field_name = f"{field_type}_{page_num + 1}_{widget_index + 1}"
            
            # Get field position and dimensions
            rect = widget.rect
            position = {
                'x': rect.x0,
                'y': rect.y0,
                'width': rect.width,
                'height': rect.height
            }
            
            # Determine field type with enhanced detection
            field_type = self.get_widget_type(widget)
            
            # Get current field value
            field_value = ""
            try:
                if hasattr(widget, 'field_value') and widget.field_value is not None:
                    field_value = str(widget.field_value)
            except:
                field_value = ""
            
            # Determine assignment based on field name and type
            assigned_to = self.determine_field_assignment(field_name, field_type)
            
            # Create a more descriptive field name by analyzing surrounding text
            display_name = self.create_display_name(field_name, field_type, position, page_text_dict, page_num)
            
            field_info = {
                'id': f"{field_name}_{page_num}_{widget_index}",
                'name': display_name,
                'pdf_field_name': field_name,  # Keep original field name for PDF operations
                'type': field_type,
                'value': field_value,
                'position': position,
                'assigned_to': assigned_to,
                'page': page_num,
                'source': 'pymupdf_widget'
            }
            
            return field_info
            
        except Exception as e:
            print(f"⚠️  Error extracting widget info: {e}")
            return None
    
    def create_display_name(self, field_name: str, field_type: str, position: dict, page_text_dict: dict, page_num: int) -> str:
        """Create a user-friendly display name for the field"""
        try:
            # Special handling for specific signature fields
            if field_type == 'signature':
                if field_name == 'signature3':
                    return 'Applicant Signature'
                elif field_name == 'property_ower_sig3':
                    return 'Property Owner Signature'
            
            # Start with a cleaned up version of the field name
            display_name = field_name.replace('_', ' ').title()
            
            # Common field name patterns and their better display names
            field_name_lower = field_name.lower()
            
            # Mapping of common field patterns to better names
            name_mappings = {
                'property_address': 'Property Address',
                'apt_num': 'Apartment Number',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'phone': 'Phone Number',
                'email': 'Email Address',
                'city': 'City',
                'state': 'State',
                'zip': 'ZIP Code',
                'signature': 'Signature',
                'date': 'Date',
                'fuel_type_elec': 'Electric Heat',
                'fuel_type_gas': 'Gas Heat',
                'fuel_type_oil': 'Oil Heat',
                'fuel_type_propane': 'Propane Heat',
                'dwelling_single_fam': 'Single Family Home',
                'dwelling_apt': 'Apartment',
                'dwelling_condo': 'Condominium',
                'owner': 'Property Owner',
                'renter': 'Renter',
                'low_income': 'Low Income Program',
                'ebt': 'EBT (Food Stamps)',
                'bill_forgive': 'Bill Forgiveness Program'
            }
            
            # Check if any mapping matches
            for pattern, better_name in name_mappings.items():
                if pattern in field_name_lower:
                    display_name = better_name
                    break
            
            # If no specific mapping found, try to find nearby text labels
            if display_name == field_name.replace('_', ' ').title():
                nearby_text = self.find_nearby_text(position, page_text_dict)
                if nearby_text and len(nearby_text) < 50:  # Reasonable label length
                    display_name = nearby_text
            
            # Add type suffix for clarity in some cases
            if field_type == 'signature' and 'signature' not in display_name.lower():
                display_name += ' (Signature)'
            elif field_type == 'checkbox' and not any(word in display_name.lower() for word in ['check', 'select', 'yes', 'no']):
                display_name += ' (Checkbox)'
            elif field_type == 'radio' and not any(word in display_name.lower() for word in ['radio', 'select', 'choose']):
                display_name += ' (Radio Button)'
            
            return display_name
            
        except Exception as e:
            print(f"⚠️  Error creating display name: {e}")
            return field_name.replace('_', ' ').title()
    
    def find_nearby_text(self, position: dict, page_text_dict: dict) -> str:
        """Find text near the field position that might be a label"""
        try:
            field_x = position['x']
            field_y = position['y']
            
            # Look for text within a reasonable distance from the field
            search_radius = 100  # pixels
            potential_labels = []
            
            for block in page_text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            span_bbox = span.get("bbox", [0, 0, 0, 0])
                            span_x = span_bbox[0]
                            span_y = span_bbox[1]
                            
                            # Calculate distance from field
                            distance = ((span_x - field_x) ** 2 + (span_y - field_y) ** 2) ** 0.5
                            
                            if distance <= search_radius:
                                text = span.get("text", "").strip()
                                if text and len(text) > 2 and len(text) < 30:
                                    potential_labels.append((distance, text))
            
            # Sort by distance and return the closest meaningful text
            if potential_labels:
                potential_labels.sort(key=lambda x: x[0])
                return potential_labels[0][1]
            
            return ""
            
        except Exception as e:
            print(f"⚠️  Error finding nearby text: {e}")
            return ""
    
    def extract_annotation_info(self, annot, page_num: int) -> Optional[Dict[str, Any]]:
        """Extract information from PDF annotations"""
        try:
            rect = annot.rect
            position = {
                'x': rect.x0,
                'y': rect.y0,
                'width': rect.width,
                'height': rect.height
            }
            
            # Determine field type based on annotation type
            annot_type = annot.type[1]
            if annot_type == 'FreeText':
                field_type = 'text'
            elif annot_type in ['Square', 'Circle']:
                field_type = 'checkbox'
            else:
                field_type = 'text'
            
            # Get annotation content
            content = annot.info.get("content", "")
            title = annot.info.get("title", "")
            
            field_name = title or f"annotation_{page_num}_{annot_type}"
            display_name = content or field_name.replace('_', ' ').title()
            
            return {
                'id': f"annot_{field_name}_{page_num}",
                'name': display_name,
                'pdf_field_name': field_name,
                'type': field_type,
                'value': content,
                'position': position,
                'assigned_to': self.determine_field_assignment(field_name, field_type),
                'page': page_num,
                'source': 'annotation'
            }
            
        except Exception as e:
            print(f"⚠️  Error extracting annotation info: {e}")
            return None
    
    def detect_text_based_fields(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect potential form fields based on text patterns"""
        try:
            text_dict = page.get_text("dict")
            fields = []
            
            # Common patterns that indicate form fields
            field_patterns = [
                # Text patterns with underscores or dashes (signature lines)
                {"pattern": r"_{5,}", "type": "text", "name": "Text Field"},
                {"pattern": r"-{5,}", "type": "text", "name": "Text Field"},
                
                # Date patterns
                {"pattern": r"date[:\s]*_{3,}", "type": "date", "name": "Date"},
                {"pattern": r"_{2,}/_{2,}/_{2,}", "type": "date", "name": "Date"},
                
                # Signature patterns
                {"pattern": r"signature[:\s]*_{5,}", "type": "signature", "name": "Signature"},
                {"pattern": r"sign[:\s]*_{5,}", "type": "signature", "name": "Signature"},
                
                # Name patterns
                {"pattern": r"name[:\s]*_{3,}", "type": "text", "name": "Name"},
                
                # Address patterns
                {"pattern": r"address[:\s]*_{3,}", "type": "text", "name": "Address"},
            ]
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_bbox = None
                        
                        # Combine all spans in the line
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            if line_bbox is None:
                                line_bbox = span.get("bbox", [0, 0, 0, 0])
                        
                        # Check against patterns
                        import re
                        for pattern_info in field_patterns:
                            if re.search(pattern_info["pattern"], line_text, re.IGNORECASE):
                                if line_bbox:
                                    position = {
                                        'x': line_bbox[0],
                                        'y': line_bbox[1],
                                        'width': line_bbox[2] - line_bbox[0],
                                        'height': line_bbox[3] - line_bbox[1]
                                    }
                                    
                                    field_name = f"text_field_{page_num}_{len(fields)}"
                                    
                                    fields.append({
                                        'id': f"text_{field_name}",
                                        'name': pattern_info["name"],
                                        'pdf_field_name': field_name,
                                        'type': pattern_info["type"],
                                        'value': '',
                                        'position': position,
                                        'assigned_to': self.determine_field_assignment(field_name, pattern_info["type"]),
                                        'page': page_num,
                                        'source': 'text_analysis'
                                    })
            
            # Remove duplicate fields that are too close to each other
            unique_fields = []
            for field in fields:
                is_duplicate = False
                for existing_field in unique_fields:
                    # Check if fields are very close to each other (likely duplicates)
                    x_diff = abs(field['position']['x'] - existing_field['position']['x'])
                    y_diff = abs(field['position']['y'] - existing_field['position']['y'])
                    if x_diff < 20 and y_diff < 20:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_fields.append(field)
            
            return unique_fields
            
        except Exception as e:
            print(f"⚠️  Error in text-based field detection: {e}")
            return []
    
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
    
    def get_widget_type(self, widget) -> str:
        """Determine the type of a PDF widget"""
        try:
            field_type_code = widget.field_type
            field_type_string = widget.field_type_string
            
            # Map field type based on PyMuPDF field types
            if field_type_code == 1:  # PDF_WIDGET_TYPE_BUTTON
                if widget.field_flags & 32768:  # Radio button
                    return 'radio'
                elif widget.field_flags & 65536:  # Checkbox
                    return 'checkbox'
                else:
                    return 'button'
            elif field_type_code == 2:  # PDF_WIDGET_TYPE_TEXT or CheckBox in some cases
                if field_type_string == 'CheckBox':
                    return 'checkbox'
                else:
                    return 'text'
            elif field_type_code == 3:  # PDF_WIDGET_TYPE_LISTBOX
                return 'select'
            elif field_type_code == 4:  # PDF_WIDGET_TYPE_COMBOBOX
                return 'select'
            elif field_type_code == 5:  # PDF_WIDGET_TYPE_SIGNATURE or RadioButton
                if field_type_string == 'RadioButton':
                    return 'radio'
                else:
                    return 'signature'
            elif field_type_code == 7:  # Text field
                # Check if this text field should be treated as a signature field
                field_name = getattr(widget, 'field_name', '').lower()
                if any(keyword in field_name for keyword in ['signature', 'sig']):
                    return 'signature'
                return 'text'
            else:
                result_type = self.supported_field_types.get(field_type_string, 'text')
                # Final check for signature fields based on field name
                field_name = getattr(widget, 'field_name', '').lower()
                if result_type == 'text' and any(keyword in field_name for keyword in ['signature', 'sig']):
                    return 'signature'
                return result_type
        except Exception as e:
            print(f"⚠️  Error determining widget type: {e}")
            return 'text'
    
    def fill_pdf_with_force_visible(self, pdf_path: str, document: Dict[str, Any], output_path: str) -> bool:
        """Fill PDF and force content to be visually present by flattening and overlaying text"""
        try:
            print(f"🎯 FORCE VISIBLE PDF FILLING: {pdf_path}")
            
            # CRITICAL FIX: Ensure pdf_fields are extracted and mapped if not present
            if 'pdf_fields' not in document or not document['pdf_fields']:
                print("📋 PDF fields not found in document, extracting and mapping...")
                
                # Extract fields
                field_extraction = self.extract_fields_with_pymupdf(pdf_path)
                if 'error' in field_extraction:
                    print(f"❌ Error extracting fields: {field_extraction['error']}")
                    return False
                
                pdf_fields = field_extraction.get('fields', [])
                
                # Map User 1 data to all fields  
                user1_data = document.get('user1_data', {})
                for field in pdf_fields:
                    field['assigned_to'] = None
                    field['value'] = ''
                    field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                    
                    # Get the actual PDF field name
                    pdf_field_name = field.get('pdf_field_name', field['name'])
                    
                    # Check if this field has a value in user1_data
                    if pdf_field_name in user1_data and user1_data[pdf_field_name]:
                        field['value'] = user1_data[pdf_field_name]
                        field['assigned_to'] = 'user1'
                        print(f"   ✅ Mapped {pdf_field_name} = {field['value']}")
                    
                    # Also check by display name mappings
                    display_name = field['name']
                    if display_name in self.field_type_map:
                        mapped_field = self.field_type_map[display_name]
                        if mapped_field in user1_data and user1_data[mapped_field]:
                            field['value'] = user1_data[mapped_field]
                            field['assigned_to'] = 'user1'
                            print(f"   ✅ Mapped {display_name} → {mapped_field} = {field['value']}")
                
                # Map frontend field names (without numbers) to PDF fields
                frontend_to_pdf_mappings = {
                    'property_address': 'property_address1',
                    'apartment_number': 'apt_num1',
                    'city': 'city1',
                    'state': 'state1',
                    'zip_code': 'zip1',
                    'first_name': 'first_name2',
                    'last_name': 'last_name2',
                    'telephone': 'phone2',
                    'email': 'email2',
                    'owner_name': 'landlord_name3',
                    'owner_address': 'address3',
                    'owner_city': 'city3',
                    'owner_state': 'text_55cits',
                    'owner_zip': 'text_56qpfj',
                    'owner_telephone': 'phone3',
                    'owner_email': 'email3'
                }
                
                for frontend_field, pdf_field in frontend_to_pdf_mappings.items():
                    if frontend_field in user1_data and user1_data[frontend_field]:
                        for field in pdf_fields:
                            if field.get('pdf_field_name') == pdf_field:
                                field['value'] = user1_data[frontend_field]
                                field['assigned_to'] = 'user1'
                                print(f"   ✅ Frontend field: {frontend_field} → {pdf_field} = {field['value']}")
                                break
                
                # Handle frontend-style array formats for Options A, B, D
                # Option A: Utility programs array
                utility_programs = user1_data.get('utility_program', [])
                if utility_programs:
                    print(f"   📋 Processing Option A utility programs: {utility_programs}")
                    program_field_mappings = {
                        'electric_discount': 'elec_discount4',
                        'matching_payment': 'matching_payment_eversource4',
                        'low_income_discount': 'low_income4',
                        'bill_forgiveness': 'bill_forgive4',
                        'matching_payment_united': 'matching_pay_united4'
                    }
                    
                    for program in utility_programs:
                        if program in program_field_mappings:
                            target_field_name = program_field_mappings[program]
                            for field in pdf_fields:
                                if field.get('pdf_field_name') == target_field_name:
                                    field['value'] = 'Yes'
                                    field['assigned_to'] = 'user1'
                                    print(f"   ✅ Option A: {program} → {target_field_name}")
                                    break
                
                # Option B: Documentation array
                documentation = user1_data.get('documentation', [])
                if documentation:
                    print(f"   📋 Processing Option B documentation: {documentation}")
                    doc_field_mappings = {
                        'ebt_award': 'ebt4',
                        'energy_assistance': 'energy_award_letter4',
                        'section_8': 'section_eight4'
                    }
                    
                    for doc in documentation:
                        if doc in doc_field_mappings:
                            target_field_name = doc_field_mappings[doc]
                            for field in pdf_fields:
                                if field.get('pdf_field_name') == target_field_name:
                                    field['value'] = 'Yes'
                                    field['assigned_to'] = 'user1'
                                    print(f"   ✅ Option B: {doc} → {target_field_name}")
                                    break
                
                # Option D: Multifamily
                if user1_data.get('qualification_option') == 'option_d':
                    print(f"   📋 Processing Option D multifamily")
                    for field in pdf_fields:
                        if field.get('pdf_field_name') == 'multifam4':
                            field['value'] = 'Yes'
                            field['assigned_to'] = 'user1'
                            print(f"   ✅ Option D: multifam4")
                            break
                
                # Map User 2 signature data
                user2_data = document.get('user2_data', {})
                for field in pdf_fields:
                    if field.get('type') == 'signature':
                        field_name = field.get('name', '')
                        field['pdf_field_name'] = field.get('pdf_field_name', field['name'])
                        field['assigned_to'] = 'user2'
                        
                        # Map Applicant Signature field
                        if 'Applicant' in field_name and user2_data.get('applicant_signature'):
                            signature_value = user2_data['applicant_signature']
                            # Check if it's base64 image data
                            if signature_value.startswith('data:image/'):
                                # For base64 images, skip form field - only overlay image
                                field['value'] = ""  # Empty form field value
                                field['is_image_signature'] = True
                                field['image_data'] = signature_value
                                print(f"🖋️  Mapped Applicant signature (image): '{field['name']}' -> [Will overlay image]")
                            else:
                                # For typed signatures, use the text directly
                                field['value'] = signature_value
                                field['is_image_signature'] = False
                                print(f"🖋️  Mapped Applicant signature (text): '{field['name']}' -> '{field['value'][:20]}...'")
                        
                        # Map Property Owner Signature field  
                        elif 'Property Owner' in field_name and user2_data.get('owner_signature'):
                            signature_value = user2_data['owner_signature']
                            # Check if it's base64 image data
                            if signature_value.startswith('data:image/'):
                                # For base64 images, skip form field - only overlay image
                                field['value'] = ""  # Empty form field value
                                field['is_image_signature'] = True
                                field['image_data'] = signature_value
                                print(f"🖋️  Mapped Property Owner signature (image): '{field['name']}' -> [Will overlay image]")
                            else:
                                # For typed signatures, use the text directly
                                field['value'] = signature_value
                                field['is_image_signature'] = False
                                print(f"🖋️  Mapped Property Owner signature (text): '{field['name']}' -> '{field['value'][:20]}...'")
                
                # Store mapped fields in document
                document['pdf_fields'] = pdf_fields
                print(f"✅ Extracted and mapped {len(pdf_fields)} fields")
            
            # Step 1: Fill PDF normally first
            temp_output = output_path.replace('.pdf', '_temp.pdf')
            success = self.fill_pdf_with_pymupdf(pdf_path, document, temp_output)
            
            if not success:
                return False
            
            # Step 2: Reopen filled PDF and add overlays
            doc = fitz.open(temp_output)
            
            # Step 3: Add image signature overlays
            print("🖼️  Adding image signature overlays...")
            doc = self.add_image_signature_overlays(doc, pdf_fields)
            
            # Step 4: Add Section 5 (Zero Income Affidavit) fields with exact positions
            if 'user2_data' in document and document['user2_data']:
                print("🧾 Adding Section 5 fields with exact positions...")
                section5_success = self.add_section5_with_exact_positions(doc, document['user2_data'])
                if section5_success:
                    print("✅ Section 5 fields added successfully")
                else:
                    print("⚠️  Section 5 fields could not be added")
            
            # Step 5: Add visual dwelling indicators if dwelling type is selected
            self.add_dwelling_visual_indicators(doc, document)
            
            # Step 6: Add visual indicators for Options A, B, D
            self.add_qualification_visual_indicators(doc, document)
            
            # Step 6: Save PDF directly (skip image conversion to preserve signature quality)
            print("🔧 Saving PDF with signatures preserved...")
            doc.save(output_path)
            doc.close()
            
            # Clean up temp file
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ FORCE VISIBLE PDF CREATED: {output_path} ({file_size:,} bytes)")
            print("🎉 Content is now permanently visible and cannot be hidden!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in force visible fill: {e}")
            import traceback
            traceback.print_exc()
            return False

    def fill_pdf_with_pymupdf(self, pdf_path: str, document: Dict[str, Any], output_path: str) -> bool:
        """Fill PDF using PyMuPDF - RESTORED TO WORKING VERSION"""
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
                        # Use field_type_map to get the actual PDF field name
                        display_name = field['name']
                        pdf_field_name = self.field_type_map.get(display_name, field.get('pdf_field_name', display_name))
                        
                        # Special handling for Date fields - map to specific widget names based on Y position
                        if display_name == 'Date' and field.get('position', {}).get('y'):
                            field_position_y = field['position']['y']
                            if 460 <= field_position_y <= 480:
                                pdf_field_name = 'date3'  # Date field near Applicant Signature
                                print(f"🎯 Mapped Date field at y={field_position_y} to widget 'date3'")
                            elif field_position_y > 630:
                                pdf_field_name = 'date_property_mang3'  # Date field near Property Owner Signature
                                print(f"🎯 Mapped Date field at y={field_position_y} to widget 'date_property_mang3'")
                        
                        # Special handling for duplicate field names - use position to disambiguate  
                        elif display_name == 'Phone Number' and field.get('position', {}).get('y'):
                            field_position_y = field['position']['y']
                            if 200 <= field_position_y <= 220:
                                pdf_field_name = 'phone_num1'  # Additional phone field at y=210
                                print(f"🎯 Mapped Phone Number field at y={field_position_y} to widget 'phone_num1'")
                            elif field_position_y > 620:
                                pdf_field_name = 'phone3'  # Landlord phone field at y=629
                                print(f"🎯 Mapped Phone Number field at y={field_position_y} to widget 'phone3'")
                        
                        elif display_name == 'City' and field.get('position', {}).get('y'):
                            field_position_y = field['position']['y']
                            if field_position_y > 590:
                                pdf_field_name = 'city3'  # Landlord city field at y=601
                                print(f"🎯 Mapped City field at y={field_position_y} to widget 'city3'")
                        
                        elif display_name == 'Email Address' and field.get('position', {}).get('y'):
                            field_position_y = field['position']['y']
                            if field_position_y > 640:
                                pdf_field_name = 'email3'  # Landlord email field at y=655
                                print(f"🎯 Mapped Email Address field at y={field_position_y} to widget 'email3'")
                        
                        # If still no mapping found, try removing suffix
                        if pdf_field_name == display_name and ' (' in display_name:
                            # Remove suffix like " (Checkbox)" or " (Radio Button)"
                            base_name = display_name.split(' (')[0]
                            pdf_field_name = base_name.lower().replace(' ', '_')
                        
                        # Exclude image signatures from field mapping to prevent base64 in form fields
                        if not field.get('is_image_signature', False) and field.get('value'):
                            field_mapping[pdf_field_name] = field['value']
                        
                        # Track signature fields separately
                        if field.get('type') == 'signature':
                            signature_fields[pdf_field_name] = {
                                'value': field['value'],
                                'position': field.get('position', {}),
                                'page': field.get('page', 0),
                                'name': field.get('name', ''),
                                'is_image_signature': field.get('is_image_signature', False),
                                'image_data': field.get('image_data', '')
                            }
            
            print(f"📋 Created field mapping with {len(field_mapping)} entries")
            print(f"🖋️  Found {len(signature_fields)} signature fields")
            
            # Fill regular form fields first
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name and (field_name in field_mapping or field_name in signature_fields):
                        # Handle signature fields with EXACT positioning and correct orientation
                        if field_name in signature_fields:
                            print(f"🎯 Processing signature field: {field_name}")
                            
                            # Skip image signatures - they'll be handled in overlay step
                            if signature_fields[field_name].get('is_image_signature', False):
                                print(f"🖼️  Skipping image signature form field: {field_name}")
                                continue
                            
                            try:
                                signature_text = signature_fields[field_name]['value']
                                # Remove "typed:" prefix if present
                                if signature_text.startswith('typed:'):
                                    signature_text = signature_text[6:].strip()
                                
                                # SIMPLIFIED APPROACH: Just set the form field value directly
                                widget.field_value = signature_text
                                widget.update()
                                print(f"✅ Set form field '{field_name}' to '{signature_text}'")
                                
                                filled_count += 1
                                continue
                            except Exception as e:
                                print(f"⚠️  Could not fill signature field '{field_name}': {e}")
                                continue
                            
                        try:
                            field_value = field_mapping[field_name]
                            
                            # Special handling for radio buttons and checkboxes
                            widget_type = self.get_widget_type(widget)
                            if widget_type == 'radio':
                                if str(field_value).lower() in ['yes', 'true', '1']:
                                    widget.field_value = True
                                    widget.update()
                                    filled_count += 1
                                    print(f"✅ Filled radio field '{field_name}' with True")
                                else:
                                    # Leave blank for "no" or "false"
                                    pass
                            elif widget_type == 'checkbox':
                                if str(field_value).lower() in ['true', 'yes', '1', 'checked']:
                                    widget.field_value = True
                                    widget.update()
                                    filled_count += 1
                                    print(f"✅ Filled checkbox field '{field_name}' with True")
                                else:
                                    widget.field_value = False
                                    widget.update()
                            else:
                                # Handle other field types normally
                                widget.field_value = str(field_value)
                                widget.update()
                                filled_count += 1
                                print(f"✅ Filled field '{field_name}' with '{field_value}'")
                        except Exception as e:
                            print(f"⚠️  Could not fill field '{field_name}': {e}")
            
            # Signature fields are now handled directly in the form field loop above
            print(f"📋 Signature fields filled directly in text boxes (no separate insertion needed)")
            
            # All fields are now filled directly in form fields - no overlays needed
            print(f"📋 All fields filled directly in PDF form fields (no overlay duplicates)")
            
            # Save the document
            doc.save(output_path)
            doc.close()
            
            print(f"✅ Successfully filled {filled_count} fields using PyMuPDF")
            return True
            
        except Exception as e:
            print(f"❌ Error filling PDF with PyMuPDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def insert_signature_text(self, page, signature_text: str, position: dict, field_name: str):
        """Simple signature text insertion - RESTORED TO WORKING VERSION"""
        try:
            x = position.get('x', 100)
            y = position.get('y', 100) 
            width = position.get('width', 200)
            height = position.get('height', 20)
            
            # Calculate text position inside the field rectangle
            text_x = x + 3  # Small left margin inside field
            text_y = y + height - 3  # 3 points from bottom of field
            
            # Simple signature text insertion with cursive font
            try:
                page.insert_text(
                    (text_x, text_y),
                    signature_text,
                    fontsize=max(10, min(height - 2, 16)),
                    color=(0, 0, 0.7),  # Dark blue color
                    fontname="times-italic"  # Cursive-style italic font
                )
                print(f"✍️  Inserted signature text '{signature_text}' for '{field_name}'")
            except:
                # Fallback to default font if italic not available
                page.insert_text(
                    (text_x, text_y),
                    signature_text,
                    fontsize=max(10, min(height - 2, 16)),
                    color=(0, 0, 0.7)
                )
                print(f"✍️  Inserted signature text '{signature_text}' for '{field_name}' (default font)")
                
        except Exception as e:
            print(f"⚠️  Error inserting signature text: {e}")
    
    def insert_signature_image(self, page, image_data: str, x: float, y: float, field_name: str):
        """Insert a base64 signature image into the PDF"""
        try:
            if not image_data or not image_data.startswith('data:image/'):
                print(f"⚠️  Invalid image data for signature '{field_name}'")
                return
            
            # Extract base64 data (remove data:image/png;base64, prefix)
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            # Convert to PIL Image
            pil_image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGBA if needed and ensure proper format
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
            
            # Resize signature to reasonable size (max 150x50 pixels)
            max_width, max_height = 150, 50
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Insert image into PDF
            img_rect = fitz.Rect(x, y - pil_image.height, x + pil_image.width, y)
            page.insert_image(img_rect, stream=img_buffer.getvalue())
            
            print(f"✍️  Inserted signature image for '{field_name}' at ({x}, {y})")
            
        except Exception as e:
            print(f"⚠️  Error inserting signature image for '{field_name}': {e}")
            # Fallback to text
            page.insert_text(
                (x, y),
                "[Signature Applied]",
                fontsize=12,
                color=(0, 0, 0.7),
                fontname="times-italic"
            )
    
    def add_image_signature_overlays(self, doc, pdf_fields: List[Dict[str, Any]]):
        """Add image signature overlays using ReportLab + PyPDF2 approach"""
        try:
            # Collect all image signatures that need to be overlaid
            image_signatures = []
            for field in pdf_fields:
                if field.get('is_image_signature', False) and field.get('image_data'):
                    field_name = field.get('name', '')
                    print(f"🖼️  Found image signature for: {field_name}")
                    
                    # Determine page and coordinates
                    page_num = field.get('page', 0)
                    
                    # Use specific coordinates for known signature fields
                    if 'Applicant' in field_name or 'applicant' in field_name.lower():
                        # Applicant signature coordinates (convert from PyMuPDF to ReportLab coords)
                        x, y = 66, 700  # ReportLab uses bottom-left origin
                        print(f"🎯 Applicant signature at ({x}, {y})")
                    elif 'Property Owner' in field_name or 'owner' in field_name.lower():
                        # Property Owner signature coordinates
                        x, y = 369, 150  # ReportLab uses bottom-left origin
                        print(f"🎯 Property Owner signature at ({x}, {y})")
                    else:
                        # Use field position if available
                        position = field.get('position', {})
                        x = position.get('x', 100)
                        y = 700 - position.get('y', 100)  # Convert coordinates
                        print(f"🎯 Generic signature at ({x}, {y})")
                    
                    image_signatures.append({
                        'field_name': field_name,
                        'image_data': field['image_data'],
                        'page_num': page_num,
                        'x': x,
                        'y': y
                    })
            
            # If we have image signatures, create overlay and merge
            if image_signatures:
                doc.save("temp_before_signatures.pdf")
                doc.close()
                
                # Create signature overlays and merge
                final_pdf_path = self.create_signature_overlays("temp_before_signatures.pdf", image_signatures)
                
                # Reopen the merged PDF
                if final_pdf_path and os.path.exists(final_pdf_path):
                    # Replace the original document with the merged one
                    import shutil
                    shutil.move(final_pdf_path, "temp_before_signatures.pdf")
                    doc = fitz.open("temp_before_signatures.pdf")
                    return doc
                    
        except Exception as e:
            print(f"⚠️  Error adding image signature overlays: {e}")
            
        return doc
    
    def create_signature_overlays(self, original_pdf_path: str, image_signatures: List[Dict[str, Any]]) -> str:
        """Create signature overlays using ReportLab and merge with PyPDF2"""
        try:
            print(f"🖼️  Creating signature overlays for {len(image_signatures)} signatures")
            
            # Read the original PDF
            original_reader = PdfReader(original_pdf_path)
            writer = PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(original_reader.pages):
                # Check if this page has any signatures
                page_signatures = [sig for sig in image_signatures if sig['page_num'] == page_num]
                
                if page_signatures:
                    print(f"📄 Page {page_num}: Adding {len(page_signatures)} signature(s)")
                    
                    # Create overlay PDF for this page using ReportLab
                    overlay_path = f"temp_signature_overlay_page_{page_num}.pdf"
                    self.create_page_signature_overlay(overlay_path, page_signatures)
                    
                    # Merge the overlay with the original page
                    if os.path.exists(overlay_path):
                        overlay_reader = PdfReader(overlay_path)
                        overlay_page = overlay_reader.pages[0]
                        page.merge_page(overlay_page)
                        
                        # Clean up overlay file
                        os.remove(overlay_path)
                
                writer.add_page(page)
            
            # Save the final merged PDF
            output_path = "temp_with_signatures.pdf"
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            print(f"✅ Created merged PDF with signatures: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠️  Error creating signature overlays: {e}")
            return None
    
    def create_page_signature_overlay(self, output_path: str, signatures: List[Dict[str, Any]]):
        """Create a transparent overlay PDF with signatures using ReportLab"""
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            
            for sig in signatures:
                print(f"🎨 Drawing signature: {sig['field_name']} at ({sig['x']}, {sig['y']})")
                
                # Decode base64 image data
                image_data = sig['image_data']
                if image_data.startswith('data:image/'):
                    # Remove data:image/png;base64, prefix
                    signature_base64 = image_data.split(",")[1]
                    signature_bytes = base64.b64decode(signature_base64)
                    signature_image = Image.open(BytesIO(signature_bytes))
                    
                    # Convert to RGBA if needed
                    if signature_image.mode != 'RGBA':
                        signature_image = signature_image.convert('RGBA')
                    
                    # Resize signature to reasonable size
                    max_width, max_height = 150, 50
                    signature_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # Create ImageReader for ReportLab
                    img_reader = ImageReader(signature_image)
                    
                    # Draw the image on the canvas
                    c.drawImage(
                        img_reader, 
                        x=sig['x'], 
                        y=sig['y'], 
                        width=signature_image.width, 
                        height=signature_image.height,
                        mask='auto'  # Handle transparency
                    )
                    
                    print(f"✅ Drew signature image {signature_image.width}x{signature_image.height}")
            
            c.save()
            print(f"💾 Saved overlay PDF: {output_path}")
            
        except Exception as e:
            print(f"⚠️  Error creating page signature overlay: {e}")
    
    def add_dwelling_visual_indicators(self, doc, document: Dict[str, Any]):
        """Add visual indicators for dwelling type selection to make it obvious"""
        try:
            # Check if dwelling type is specified
            user1_data = document.get('user1_data', {})
            dwelling_type = user1_data.get('dwelling_type')
            
            # If no dwelling_type field, check individual checkbox fields
            if not dwelling_type:
                if user1_data.get('dwelling_single_fam1') == 'Yes':
                    dwelling_type = 'single_family'
                elif user1_data.get('dwelling_apt1') == 'Yes':
                    dwelling_type = 'apartment'
                elif user1_data.get('dwelling_condo1') == 'Yes':
                    dwelling_type = 'condominium'
                else:
                    return
            
            print(f"🏠 Adding visual indicators for dwelling type: {dwelling_type}")
            
            # Get page 3 where dwelling checkboxes are located
            if len(doc) >= 3:
                page = doc[2]  # Page 3 (0-indexed)
                
                # Define dwelling type positions - MUCH LOWER AND NARROWER
                # PDF coordinates: (0,0) = BOTTOM-LEFT, so high Y values = top of page
                # Original checkboxes are at y=256-280, page height is ~792
                # User wants: much lower than y=650 and much narrower than w=80
                dwelling_positions = {
                    'single_family': {'x': 55.0, 'y': 440.0, 'w': 8.0, 'h': 8.0},   # Top position, moved tiny bit lower
                    'apartment': {'x': 55.0, 'y': 425.0, 'w': 8.0, 'h': 8.0},      # Middle position, same
                    'condominium': {'x': 55.0, 'y': 410.0, 'w': 8.0, 'h': 8.0}     # Bottom position, same
                }
                
                dwelling_labels = {
                    'single_family': 'Single Family Home',
                    'apartment': 'Apartment',
                    'condominium': 'Condominium'
                }
                
                # Add visual indicators for each dwelling type
                for dtype, pos in dwelling_positions.items():
                    x, y, w, h = pos['x'], pos['y'], pos['w'], pos['h']
                    label = dwelling_labels.get(dtype, dtype)
                    
                    if dtype == dwelling_type or dwelling_type == 'all':
                        # Selected dwelling - add checkmark in checkbox
                        try:
                            # Draw checkbox outline
                            checkbox_rect = fitz.Rect(x, y, x + w, y + h)
                            page.draw_rect(checkbox_rect, color=(0, 0, 0), width=1)
                            
                            # Add checkmark symbol inside the checkbox
                            try:
                                # Draw a checkmark using lines
                                # Checkmark is made of two lines forming a "✓"
                                check_size = min(w, h) * 0.6
                                center_x = x + w/2
                                center_y = y + h/2
                                
                                # First line of checkmark (bottom left to middle)
                                p1 = fitz.Point(center_x - check_size/2, center_y)
                                p2 = fitz.Point(center_x - check_size/4, center_y - check_size/2)
                                page.draw_line(p1, p2, color=(0, 0, 0), width=1.5)
                                
                                # Second line of checkmark (middle to top right)
                                p3 = fitz.Point(center_x - check_size/4, center_y - check_size/2)
                                p4 = fitz.Point(center_x + check_size/2, center_y + check_size/2)
                                page.draw_line(p3, p4, color=(0, 0, 0), width=1.5)
                                
                            except:
                                # Fallback: simple "X" mark
                                page.insert_text(
                                    (x + 1, y + h - 1),
                                    "✓",
                                    fontsize=6,
                                    color=(0, 0, 0)
                                )
                            
                            print(f"   ✅ Added checkbox with checkmark for {label} at y={y}")
                            
                        except Exception as e:
                            print(f"   ❌ Error adding checkbox for {dtype}: {e}")
                    else:
                        # Unselected dwelling - add subtle indicator
                        try:
                            # Add gray circle to show it's unselected
                            center = fitz.Point(x + w/2, y + h/2)
                            page.draw_circle(center, w * 1.2, color=(0.7, 0.7, 0.7), width=1)
                            print(f"   ✅ Added unselected indicator for {label}")
                        except Exception as e:
                            print(f"   ❌ Error adding unselected indicator for {dtype}: {e}")
                
        except Exception as e:
            print(f"❌ Error adding dwelling visual indicators: {e}")
    
    def add_qualification_visual_indicators(self, doc, document: Dict[str, Any]):
        """Add visual indicators for Options A, B, D qualification checkboxes"""
        try:
            user1_data = document.get('user1_data', {})
            
            # Check which options are selected
            selected_options = []
            
            # Option A programs
            option_a_programs = []
            utility_programs = user1_data.get('utility_program', [])
            if utility_programs:
                option_a_programs.extend(utility_programs)
            
            # Also check direct field values
            if user1_data.get('elec_discount4') == 'Yes':
                option_a_programs.append('electric_discount')
            if user1_data.get('low_income4') == 'Yes':
                option_a_programs.append('low_income_discount')
            if user1_data.get('matching_payment_eversource4') == 'Yes':
                option_a_programs.append('matching_payment')
            if user1_data.get('bill_forgive4') == 'Yes':
                option_a_programs.append('bill_forgiveness')
            if user1_data.get('matching_pay_united4') == 'Yes':
                option_a_programs.append('matching_payment_united')
            
            # Option B documentation
            option_b_docs = []
            documentation = user1_data.get('documentation', [])
            if documentation:
                option_b_docs.extend(documentation)
            
            # Also check direct field values
            if user1_data.get('ebt4') == 'Yes':
                option_b_docs.append('ebt_award')
            if user1_data.get('energy_award_letter4') == 'Yes':
                option_b_docs.append('energy_assistance')
            if user1_data.get('section_eight4') == 'Yes':
                option_b_docs.append('section_8')
            
            # Option D multifamily
            option_d_selected = (user1_data.get('qualification_option') == 'option_d' or 
                               user1_data.get('multifam4') == 'Yes')
            
            # Only add indicators if there are selections
            if not (option_a_programs or option_b_docs or option_d_selected):
                return
            
            print(f"📋 Adding visual indicators for qualification options:")
            if option_a_programs:
                print(f"   Option A: {option_a_programs}")
            if option_b_docs:
                print(f"   Option B: {option_b_docs}")
            if option_d_selected:
                print(f"   Option D: multifamily")
            
            # Get page 4 where qualification checkboxes are located
            if len(doc) >= 4:
                page = doc[3]  # Page 4 (0-indexed)
                
                # Define checkbox positions based on actual PDF widget locations
                # Adjusted Y positions to be higher - PDF coordinates (0,0) = bottom-left
                qualification_positions = {
                    # Option A positions (left column) - moved another 5 points higher
                    'elec_discount4': {'x': 55.0, 'y': 490.0, 'w': 8.0, 'h': 8.0},
                    'matching_payment_eversource4': {'x': 55.0, 'y': 472.0, 'w': 8.0, 'h': 8.0},
                    
                    # Option A positions (right column) - adjusted slightly right
                    'low_income4': {'x': 208.0, 'y': 490.0, 'w': 8.0, 'h': 8.0},
                    'bill_forgive4': {'x': 208.0, 'y': 477.0, 'w': 8.0, 'h': 8.0},
                    'matching_pay_united4': {'x': 208.0, 'y': 458.0, 'w': 8.0, 'h': 8.0},
                    
                    # Option B positions - moved 15 points higher and to the right
                    'ebt4': {'x': 56.0, 'y': 393.0, 'w': 8.0, 'h': 8.0},
                    'energy_award_letter4': {'x': 56.0, 'y': 378.0, 'w': 8.0, 'h': 8.0},
                    'section_eight4': {'x': 56.0, 'y': 362.0, 'w': 8.0, 'h': 8.0},
                    
                    # Option D position - moved 1 to the right
                    'multifam4': {'x': 423.0, 'y': 334.0, 'w': 8.0, 'h': 8.0}
                }
                
                # Map frontend programs to PDF field names
                program_to_field = {
                    'electric_discount': 'elec_discount4',
                    'low_income_discount': 'low_income4',
                    'matching_payment': 'matching_payment_eversource4',
                    'bill_forgiveness': 'bill_forgive4',
                    'matching_payment_united': 'matching_pay_united4',
                    'ebt_award': 'ebt4',
                    'energy_assistance': 'energy_award_letter4',
                    'section_8': 'section_eight4'
                }
                
                # Add visual indicators for selected Option A programs
                for program in option_a_programs:
                    field_name = program_to_field.get(program)
                    if field_name and field_name in qualification_positions:
                        pos = qualification_positions[field_name]
                        self.draw_checkbox_indicator(page, pos, f"Option A: {program}")
                
                # Add visual indicators for selected Option B docs
                for doc in option_b_docs:
                    field_name = program_to_field.get(doc)
                    if field_name and field_name in qualification_positions:
                        pos = qualification_positions[field_name]
                        self.draw_checkbox_indicator(page, pos, f"Option B: {doc}")
                
                # Add visual indicator for Option D
                if option_d_selected:
                    pos = qualification_positions['multifam4']
                    self.draw_checkbox_indicator(page, pos, "Option D: multifamily")
                        
        except Exception as e:
            print(f"⚠️  Error adding qualification visual indicators: {e}")
    
    def draw_checkbox_indicator(self, page, position: dict, label: str):
        """Draw a checkbox with checkmark indicator"""
        try:
            x, y, w, h = position['x'], position['y'], position['w'], position['h']
            
            # Draw checkbox outline
            checkbox_rect = fitz.Rect(x, y, x + w, y + h)
            page.draw_rect(checkbox_rect, color=(0, 0, 0), width=1)
            
            # Add checkmark symbol inside the checkbox
            check_size = min(w, h) * 0.6
            center_x = x + w/2
            center_y = y + h/2
            
            # First line of checkmark (bottom left to middle)
            p1 = fitz.Point(center_x - check_size/2, center_y)
            p2 = fitz.Point(center_x - check_size/4, center_y - check_size/2)
            page.draw_line(p1, p2, color=(0, 0, 0), width=1.5)
            
            # Second line of checkmark (middle to top right)
            p3 = fitz.Point(center_x - check_size/4, center_y - check_size/2)
            p4 = fitz.Point(center_x + check_size/2, center_y + check_size/2)
            page.draw_line(p3, p4, color=(0, 0, 0), width=1.5)
            
            print(f"   ✅ Added checkbox indicator for {label} at ({x}, {y})")
            
        except Exception as e:
            print(f"⚠️  Error drawing checkbox indicator for {label}: {e}")
    
    def convert_pdf_to_image(self, pdf_path: str, page_num: int = 0) -> str:
        """Convert PDF page to base64 image for preview"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            if page_num >= len(doc):
                page_num = 0
                
            page = doc[page_num]
            
            # Convert page to image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PNG bytes
            img_data = pix.tobytes("png")
            
            # Convert to base64 for web display
            import base64
            img_base64 = base64.b64encode(img_data).decode()
            
            doc.close()
            
            # Return as data URL
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"❌ Error converting PDF to image: {e}")
            return "/static/placeholder-pdf.png"
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get PDF information including page count"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            info = {
                'page_count': len(doc),
                'width': doc[0].rect.width if len(doc) > 0 else 0,
                'height': doc[0].rect.height if len(doc) > 0 else 0,
                'file_size': os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
            }
            
            doc.close()
            return info
            
        except Exception as e:
            print(f"❌ Error getting PDF info: {e}")
            return {'page_count': 1, 'width': 612, 'height': 792, 'file_size': 0}

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
    
    def add_section5_with_exact_positions(self, doc, user2_data):
        """Add Section 5 (Zero Income Affidavit) fields with exact positions"""
        try:
            # Section 5 Widget Positions - Same as in app.py
            SECTION5_WIDGET_POSITIONS = [
                {"field": "account_holder_name_affidavit", "x": 155, "y": 145, "width": 250, "height": 25},
                {"field": "household_member_names_no_income", "x": 45, "y": 265, "width": 450, "height": 80},
                {"field": "affidavit_signature", "x": 40, "y": 490, "width": 200, "height": 30},
                {"field": "printed_name_affidavit", "x": 315, "y": 490, "width": 230, "height": 25},
                {"field": "date_affidavit", "x": 50, "y": 535, "width": 150, "height": 25},
                {"field": "telephone_affidavit", "x": 315, "y": 535, "width": 150, "height": 25}
            ]
            
            # Find the Zero Income Affidavit page (usually page 5)
            affidavit_page = None
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().lower()
                if "zero income affidavit" in text or "income affidavit" in text:
                    affidavit_page = page_num
                    break
            
            if affidavit_page is None:
                # Default to last page
                affidavit_page = len(doc) - 1
            
            page = doc[affidavit_page]
            print(f"📄 Adding Section 5 fields to page {affidavit_page + 1}")
            
            # Map user2_data to Section 5 fields
            section5_mapping = {
                "account_holder_name_affidavit": user2_data.get("account_holder_name_affidavit", ""),
                "household_member_names_no_income": user2_data.get("household_member_names_no_income", ""),
                "affidavit_signature": user2_data.get("affidavit_signature", ""),
                "printed_name_affidavit": user2_data.get("printed_name_affidavit", ""),
                "date_affidavit": user2_data.get("date_affidavit", ""),
                "telephone_affidavit": user2_data.get("telephone_affidavit", "")
            }
            
            filled_count = 0
            
            # Fill each Section 5 field at exact position
            for pos in SECTION5_WIDGET_POSITIONS:
                field_name = pos["field"]
                field_value = section5_mapping.get(field_name, "")
                
                if field_value:
                    x, y, width, height = pos["x"], pos["y"], pos["width"], pos["height"]
                    
                    # Determine font size and style based on field type
                    if field_name == "household_member_names_no_income":
                        fontsize = 9  # Smaller for multi-line text
                        fontname = "helv"
                    elif field_name == "affidavit_signature":
                        fontsize = 11
                        fontname = "times-italic"  # Cursive font for signature
                    else:
                        fontsize = 11
                        fontname = "helv"
                    
                    # Use the same method as the working app.py version
                    rect = fitz.Rect(x, y, x + width, y + height)
                    
                    # Add freetext annotation with appropriate font
                    text_annot = page.add_freetext_annot(
                        rect,
                        field_value,
                        fontsize=fontsize,
                        fontname=fontname,
                        text_color=(0, 0, 0.7) if field_name == "affidavit_signature" else (0, 0, 0),  # Blue for signatures
                        fill_color=(1, 1, 1),  # White background
                        border_color=(0, 0, 0)
                    )
                    text_annot.update()
                    
                    filled_count += 1
                    print(f"   ✅ Section 5 field positioned: {field_name} = {field_value}")
            
            print(f"📄 Section 5: Filled {filled_count} fields using exact positions on page {affidavit_page + 1}")
            return filled_count > 0
            
        except Exception as e:
            print(f"❌ Error adding Section 5 with exact positions: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
                
                # Special handling for signature fields using the same fixed positioning
                if field.get('type') == 'signature' and field.get('value'):
                    signature_text = field['value']
                    field_name = field.get('name', '')
                    
                    # Calculate coordinates first
                    if field_name in ['Applicant Signature', 'signature3']:
                        signature_x = 66
                        signature_y = 152
                        print(f"🎯 Overlay: Applicant Signature at ({signature_x}, {signature_y})")
                    elif field_name in ['Property Owner Signature', 'property_ower_sig3']:
                        # Use visible coordinates within the page bounds
                        signature_x = 369  # Widget start (319) + 50 pixels right
                        signature_y = 622  # Widget start (612) + 10 pixels down
                        print(f"🎯 Overlay: Property Owner Signature at ({signature_x}, {signature_y})")
                    else:
                        # Fallback positioning for other signature fields
                        signature_x = position.get('x', 0)
                        signature_y = position.get('y', 0) + 12
                    
                    # Handle image signatures by inserting the actual image
                    if field.get('is_image_signature', False):
                        print(f"🖼️  Processing image signature for '{field_name}'")
                        self.insert_signature_image(page, field.get('image_data'), signature_x, signature_y, field_name)
                        continue
                    
                    # Insert signature with proper orientation and cursive font
                    try:
                        page.insert_text(
                            (signature_x, signature_y),
                            signature_text,
                            fontsize=10,
                            color=(0, 0, 0.8),  # Dark blue for signatures
                            fontname="times-italic",  # Cursive-style font
                            morph=(fitz.Point(signature_x, signature_y), fitz.Matrix(1, 0, 0, -1, 0, 0))
                        )
                        print(f"✅ Added overlay signature '{signature_text}' at ({signature_x}, {signature_y})")
                    except Exception as sig_error:
                        # Fallback without matrix transformation
                        page.insert_text(
                            (signature_x, signature_y),
                            signature_text,
                            fontsize=10,
                            color=(0, 0, 0.8),
                            fontname="times-italic"  # Cursive-style font
                        )
                        print(f"✅ Added overlay signature '{signature_text}' (fallback) at ({signature_x}, {signature_y})")
                else:
                    # Regular text fields
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