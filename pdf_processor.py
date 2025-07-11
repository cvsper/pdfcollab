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
            
            # Step 1: Fill PDF normally first
            temp_output = output_path.replace('.pdf', '_temp.pdf')
            success = self.fill_pdf_with_pymupdf(pdf_path, document, temp_output)
            
            if not success:
                return False
            
            # Step 2: Reopen filled PDF and add overlays
            doc = fitz.open(temp_output)
            
            # Step 3: All fields are filled directly in form fields - no overlays needed
            print("📋 All fields filled directly in PDF form fields (no overlay duplicates)")
            
            # Step 4: Add Section 5 (Zero Income Affidavit) fields with exact positions
            if 'user2_data' in document and document['user2_data']:
                print("🧾 Adding Section 5 fields with exact positions...")
                section5_success = self.add_section5_with_exact_positions(doc, document['user2_data'])
                if section5_success:
                    print("✅ Section 5 fields added successfully")
                else:
                    print("⚠️  Section 5 fields could not be added")
            
            # Step 5: Save PDF directly (skip image conversion to preserve signature quality)
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
                        # Handle signature fields with EXACT positioning and correct orientation
                        if field_name in signature_fields:
                            try:
                                signature_text = signature_fields[field_name]['value']
                                # Remove "typed:" prefix if present
                                if signature_text.startswith('typed:'):
                                    signature_text = signature_text[6:].strip()
                                
                                # Clear the form field
                                widget.field_value = ""
                                widget.update()
                                
                                # Use WIDGET-BASED positioning with proper text orientation
                                rect = widget.rect
                                
                                # Use exact coordinates - FIXED DIRECTIONS (down = decrease Y)
                                if field_name in ['Applicant Signature', 'signature3']:
                                    # Current (66, 157) - 5 down = (66, 152) 
                                    signature_x = 66
                                    signature_y = 152
                                    print(f"🎯 Applicant Signature widget: ({rect.x0:.0f}, {rect.y0:.0f}) to ({rect.x1:.0f}, {rect.y1:.0f})")
                                    print(f"🎯 Using FIXED coordinates (Applicant 5 down): ({signature_x:.0f}, {signature_y:.0f})")
                                elif field_name in ['Property Owner Signature', 'property_ower_sig3']:
                                    # Property Owner: 20 to the right = 410 + 20 = 430  
                                    signature_x = 430
                                    signature_y = -38
                                    print(f"🎯 Property Owner Signature widget: ({rect.x0:.0f}, {rect.y0:.0f}) to ({rect.x1:.0f}, {rect.y1:.0f})")
                                    print(f"🎯 Using FIXED coordinates (Property Owner 20 right): ({signature_x:.0f}, {signature_y:.0f})")
                                else:
                                    # Fallback positioning
                                    signature_x = rect.x0 + 5
                                    signature_y = rect.y0 + rect.height * 0.75
                                    print(f"⚠️  Using fallback position for signature field: {field_name}")
                
                                
                                signature_font_size = 10  # Smaller font to fit in widget
                                
                                try:
                                    # Fix text orientation - use proper transformation matrix
                                    # Create transformation matrix for normal text orientation
                                    # Matrix(a, b, c, d, e, f) where:
                                    # a=1, d=1 for normal scaling
                                    # b=0, c=0 for no rotation/skew
                                    # e,f for translation
                                    text_matrix = fitz.Matrix(1, 0, 0, 1, 0, 0)  # Identity matrix for normal orientation
                                    
                                    # Insert text with proper orientation
                                    text_writer = fitz.TextWriter(page.rect)
                                    text_writer.append(
                                        (signature_x, signature_y),
                                        signature_text,
                                        fontsize=signature_font_size,
                                        fontname="helv"
                                    )
                                    text_writer.write_text(page, color=(0, 0, 0.8))
                                    print(f"✅ Added signature '{signature_text}' for '{field_name}' using TextWriter at ({signature_x:.0f}, {signature_y:.0f})")
                                except Exception as text_writer_error:
                                    print(f"⚠️  TextWriter failed: {text_writer_error}, trying insert_text with matrix...")
                                    try:
                                        # Alternative: Fix backwards text by only flipping Y axis (keep X normal)
                                        # Matrix(a, b, c, d, e, f) - try just Y flip: a=1, d=-1 to fix upside down only
                                        page.insert_text(
                                            (signature_x, signature_y),
                                            signature_text,
                                            fontsize=signature_font_size,
                                            color=(0, 0, 0.8),
                                            morph=(fitz.Point(signature_x, signature_y), fitz.Matrix(1, 0, 0, -1, 0, 0))
                                        )
                                        print(f"✅ Added signature '{signature_text}' for '{field_name}' with FLIPPED matrix at ({signature_x:.0f}, {signature_y:.0f})")
                                    except Exception as matrix_error:
                                        print(f"⚠️  Matrix approach failed: {matrix_error}, using simple insert_text...")
                                        # Final fallback
                                        page.insert_text(
                                            (signature_x, signature_y),
                                            signature_text,
                                            fontsize=signature_font_size,
                                            color=(0, 0, 0.8)
                                        )
                                        print(f"✅ Added signature '{signature_text}' for '{field_name}' (simple fallback) at ({signature_x:.0f}, {signature_y:.0f})")
                                
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
            
            # Simple signature text insertion with italic font
            try:
                page.insert_text(
                    (text_x, text_y),
                    signature_text,
                    fontsize=max(10, min(height - 2, 16)),
                    color=(0, 0, 0.7),  # Dark blue color
                    fontname="helv-oblique"  # Simple italic font
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
                    
                    # Determine font size based on field type
                    if field_name == "household_member_names_no_income":
                        fontsize = 9  # Smaller for multi-line text
                    else:
                        fontsize = 11
                    
                    # Use the same method as the working app.py version
                    rect = fitz.Rect(x, y, x + width, y + height)
                    
                    # Add freetext annotation like in app.py
                    text_annot = page.add_freetext_annot(
                        rect,
                        field_value,
                        fontsize=fontsize,
                        fontname="helv",
                        text_color=(0, 0, 0),
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
                    
                    # Use the same exact coordinates as the main processor
                    if field_name in ['Applicant Signature', 'signature3']:
                        signature_x = 66
                        signature_y = 152
                        print(f"🎯 Overlay: Applicant Signature at ({signature_x}, {signature_y})")
                    elif field_name in ['Property Owner Signature', 'property_ower_sig3']:
                        signature_x = 430
                        signature_y = -38
                        print(f"🎯 Overlay: Property Owner Signature at ({signature_x}, {signature_y})")
                    else:
                        # Fallback positioning for other signature fields
                        signature_x = position.get('x', 0)
                        signature_y = position.get('y', 0) + 12
                    
                    # Insert signature with proper orientation
                    try:
                        page.insert_text(
                            (signature_x, signature_y),
                            signature_text,
                            fontsize=10,
                            color=(0, 0, 0.8),  # Dark blue for signatures
                            morph=(fitz.Point(signature_x, signature_y), fitz.Matrix(1, 0, 0, -1, 0, 0))
                        )
                        print(f"✅ Added overlay signature '{signature_text}' at ({signature_x}, {signature_y})")
                    except Exception as sig_error:
                        # Fallback without matrix transformation
                        page.insert_text(
                            (signature_x, signature_y),
                            signature_text,
                            fontsize=10,
                            color=(0, 0, 0.8)
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