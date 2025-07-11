#!/usr/bin/env python3
"""
Improved PDF processor with exact field mapping for accurate placement
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List
from field_mapping_config import FIELD_MAPPING_CONFIG, SECTION5_EXACT_POSITIONS, get_pdf_field_for_form_field

class ImprovedPDFProcessor:
    """Enhanced PDF processor with exact field mapping"""
    
    def __init__(self):
        self.field_mappings = FIELD_MAPPING_CONFIG
        self.section5_positions = SECTION5_EXACT_POSITIONS
    
    def fill_pdf_with_exact_mapping(self, pdf_path: str, user1_data: dict, user2_data: dict, output_path: str):
        """Fill PDF using exact field mappings to ensure correct placement"""
        
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            print(f"📖 Opened PDF: {pdf_path} ({len(doc)} pages)")
            
            # Combine all form data
            all_data = {**user1_data, **user2_data}
            
            # Track filled fields
            filled_count = 0
            section5_fields = []
            unmapped_fields = []
            
            print(f"📋 Processing {len(all_data)} form fields")
            
            # Process each form field with exact mapping
            for form_field, value in all_data.items():
                if not value:  # Skip empty values
                    continue
                
                mapping = get_pdf_field_for_form_field(form_field)
                
                if not mapping:
                    unmapped_fields.append(form_field)
                    continue
                
                # Handle Section 5 fields separately (they don't have PDF form fields)
                if form_field in self.section5_positions:
                    section5_fields.append({'field': form_field, 'value': value})
                    continue
                
                # Fill regular PDF form fields
                success = self._fill_pdf_form_field(doc, mapping, value, form_field)
                if success:
                    filled_count += 1
                    print(f"   ✅ {form_field}: '{value}' → {mapping['pdf_field_name']}")
                else:
                    print(f"   ❌ Failed to fill {form_field}")
            
            # Handle Section 5 fields with exact positioning
            if section5_fields:
                section5_count = self._add_section5_fields(doc, section5_fields)
                filled_count += section5_count
                print(f"📄 Added {section5_count} Section 5 fields with exact positioning")
            
            # Report results
            if unmapped_fields:
                print(f"⚠️  Unmapped fields: {', '.join(unmapped_fields)}")
            
            print(f"✅ Successfully filled {filled_count} fields")
            
            # Save the filled PDF
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling PDF: {e}")
            return False
    
    def _fill_pdf_form_field(self, doc: fitz.Document, mapping: dict, value: str, form_field: str) -> bool:
        """Fill a specific PDF form field using exact mapping"""
        
        try:
            page_num = mapping['page']
            pdf_field_name = mapping['pdf_field_name']
            field_type = mapping['type']
            
            # Get the page
            if page_num >= len(doc):
                print(f"⚠️  Page {page_num} not found for field {form_field}")
                return False
            
            page = doc[page_num]
            
            # Find the specific field on the page
            widgets = list(page.widgets())
            target_widget = None
            
            for widget in widgets:
                # Try different ways to get field name
                widget_name = ''
                if hasattr(widget, 'field_name'):
                    widget_name = widget.field_name
                elif hasattr(widget, 'field_label'):
                    widget_name = widget.field_label
                
                # Debug: print actual field name
                print(f"   🔍 Checking widget: '{widget_name}' vs target: '{pdf_field_name}'")
                
                if widget_name == pdf_field_name:
                    target_widget = widget
                    break
            
            if not target_widget:
                print(f"⚠️  PDF field '{pdf_field_name}' not found on page {page_num + 1}")
                return False
            
            # Set the field value based on type
            if field_type == 'text' or field_type == 'signature':
                target_widget.field_value = str(value)
                target_widget.update()
                
            elif field_type == 'checkbox':
                # For checkboxes, value should be True/False or 'on'/'off'
                if str(value).lower() in ['true', '1', 'on', 'yes']:
                    target_widget.field_value = True
                else:
                    target_widget.field_value = False
                target_widget.update()
                
            elif field_type == 'radio':
                # For radio buttons, set the value if it matches
                if str(value).lower() in ['true', '1', 'on', 'yes']:
                    target_widget.field_value = True
                    target_widget.update()
            
            return True
            
        except Exception as e:
            print(f"❌ Error filling field {form_field}: {e}")
            return False
    
    def _add_section5_fields(self, doc: fitz.Document, section5_fields: List[dict]) -> int:
        """Add Section 5 fields using exact positioning"""
        
        try:
            # Section 5 is on page 5 (index 4)
            page = doc[4]
            filled_count = 0
            
            for field_data in section5_fields:
                field_name = field_data['field']
                field_value = field_data['value']
                
                if field_name not in self.section5_positions:
                    continue
                
                pos = self.section5_positions[field_name]
                x, y, width, height = pos['x'], pos['y'], pos['width'], pos['height']
                
                # Determine font size
                fontsize = 9 if field_name == 'household_member_names_no_income' else 11
                
                # Add text annotation at exact position
                rect = fitz.Rect(x, y, x + width, y + height)
                text_annot = page.add_freetext_annot(
                    rect,
                    field_value,
                    fontsize=fontsize,
                    fontname="helv",
                    text_color=(0, 0, 0),
                    fill_color=(1, 1, 1),
                    border_color=(0, 0, 0)
                )
                text_annot.update()
                filled_count += 1
                
                print(f"   ✅ Section 5: {field_name} = {field_value} at ({x}, {y})")
            
            return filled_count
            
        except Exception as e:
            print(f"❌ Error adding Section 5 fields: {e}")
            return 0
    
    def validate_mappings_against_pdf(self, pdf_path: str):
        """Validate that all mapped PDF fields actually exist in the PDF"""
        
        try:
            doc = fitz.open(pdf_path)
            all_pdf_fields = []
            
            # Extract all PDF field names
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = list(page.widgets())
                
                for widget in widgets:
                    # Get field name from widget
                    field_name = 'Unnamed'
                    if hasattr(widget, 'field_name') and widget.field_name:
                        field_name = widget.field_name
                    elif hasattr(widget, 'field_label') and widget.field_label:
                        field_name = widget.field_label
                    
                    all_pdf_fields.append({
                        'name': field_name,
                        'page': page_num,
                        'type': widget.field_type_string if hasattr(widget, 'field_type_string') else 'unknown'
                    })
            
            doc.close()
            
            # Check if all mapped fields exist
            missing_fields = []
            for form_field, mapping in self.field_mappings.items():
                pdf_field_name = mapping['pdf_field_name']
                expected_page = mapping['page']
                
                found = False
                for pdf_field in all_pdf_fields:
                    if pdf_field['name'] == pdf_field_name and pdf_field['page'] == expected_page:
                        found = True
                        break
                
                if not found:
                    missing_fields.append({
                        'form_field': form_field,
                        'pdf_field': pdf_field_name,
                        'page': expected_page
                    })
            
            if missing_fields:
                print(f"⚠️  Missing PDF fields:")
                for missing in missing_fields:
                    print(f"   • {missing['form_field']} → {missing['pdf_field']} (page {missing['page'] + 1})")
                return False
            else:
                print(f"✅ All {len(self.field_mappings)} mapped fields found in PDF")
                return True
                
        except Exception as e:
            print(f"❌ Error validating mappings: {e}")
            return False

def test_improved_processor():
    """Test the improved PDF processor"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return False
    
    # Test data
    user1_data = {
        'property_address': '123 Test Street',
        'apartment_number': 'Unit 5B',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'first_name': 'John',
        'last_name': 'Doe',
        'telephone': '(860) 555-1234',
        'email': 'john.doe@example.com',
        'household_size': '3',
        'adults_count': '2',
        'annual_income': '45000'
    }
    
    user2_data = {
        'applicant_signature': 'John Doe',
        'authorization_date': '2025-07-11',
        'account_holder_name_affidavit': 'John Doe',
        'affidavit_signature': 'John Doe',
        'printed_name_affidavit': 'JOHN DOE',
        'date_affidavit': '2025-07-11',
        'telephone_affidavit': '(860) 555-1234'
    }
    
    # Create output path
    output_path = os.path.join(os.path.dirname(__file__), 'test_improved_output.pdf')
    
    # Test the processor
    processor = ImprovedPDFProcessor()
    
    print("🧪 Testing Improved PDF Processor")
    print("=" * 50)
    
    # Validate mappings first
    print("📋 Validating field mappings...")
    if not processor.validate_mappings_against_pdf(homeworks_path):
        print("❌ Field mapping validation failed")
        return False
    
    # Fill the PDF
    print("\n📝 Filling PDF with test data...")
    success = processor.fill_pdf_with_exact_mapping(
        homeworks_path, user1_data, user2_data, output_path
    )
    
    if success:
        print(f"\n✅ Success! Test PDF created: {output_path}")
        return True
    else:
        print(f"\n❌ Failed to create test PDF")
        return False

if __name__ == "__main__":
    test_improved_processor()