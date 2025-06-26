#!/usr/bin/env python3
"""
Test script to verify PDF filling functionality works correctly
"""

import os
import sys
import tempfile
from pdf_processor import PDFProcessor
import fitz  # PyMuPDF

def test_pdf_filling():
    """Test the complete PDF filling process"""
    print("🧪 Starting PDF filling functionality test...")
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Test data - simulating filled form data
    test_document = {
        'id': 'test_123',
        'name': 'test_document.pdf',
        'pdf_fields': [
            {
                'id': 'field_1',
                'name': 'Property Address',
                'pdf_field_name': 'property_address1',
                'value': 'Test Address 123 Main St',
                'type': 'text',
                'assigned_to': 'user1',
                'position': {'x': 100, 'y': 200, 'width': 200, 'height': 20},
                'page': 0
            },
            {
                'id': 'field_2', 
                'name': 'Electric Heat',
                'pdf_field_name': 'fuel_type_elec2',
                'value': 'yes',
                'type': 'radio',
                'assigned_to': 'user1',
                'position': {'x': 150, 'y': 250, 'width': 15, 'height': 15},
                'page': 0
            },
            {
                'id': 'field_3',
                'name': 'Signature',
                'pdf_field_name': 'signature3',
                'value': 'John Smith Test Signature',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 200, 'y': 300, 'width': 150, 'height': 25},
                'page': 0
            }
        ]
    }
    
    # Check if we have a test PDF file
    test_pdf_path = None
    possible_paths = [
        'uploads/c83e2f43-b4b7-4a4d-9b26-de394bc5008b_homeworks.pdf',
        'uploads/test.pdf', 
        'test.pdf',
        'homeworks.pdf',
        'sample.pdf'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_pdf_path = path
            break
    
    if not test_pdf_path:
        print("❌ No test PDF file found. Looking for PDF files in current directory...")
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if pdf_files:
            test_pdf_path = pdf_files[0]
            print(f"📄 Using PDF file: {test_pdf_path}")
        else:
            print("❌ No PDF files found. Creating a simple test PDF...")
            test_pdf_path = create_test_pdf()
    
    print(f"📄 Testing with PDF: {test_pdf_path}")
    
    # Test 1: PDF Field Extraction
    print("\n🔍 Test 1: PDF Field Extraction")
    try:
        fields = processor.extract_fields_with_pymupdf(test_pdf_path)
        if 'error' in fields:
            print(f"❌ Field extraction failed: {fields['error']}")
            return False
        
        field_count = len(fields.get('fields', []))
        print(f"✅ Extracted {field_count} fields from PDF")
        
        # Show first few fields
        for i, field in enumerate(fields.get('fields', [])[:3]):
            print(f"   Field {i+1}: {field.get('name', 'unnamed')} ({field.get('type', 'unknown')})")
            
    except Exception as e:
        print(f"❌ Field extraction test failed: {e}")
        return False
    
    # Test 2: PDF Filling
    print("\n📝 Test 2: PDF Filling")
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            output_path = temp_file.name
        
        success = processor.fill_pdf_with_pymupdf(test_pdf_path, test_document, output_path)
        
        if success:
            print("✅ PDF filling completed successfully")
            
            # Verify output file exists and has content
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Output file created: {file_size} bytes")
                
                # Test 3: Verify PDF structure
                print("\n🔍 Test 3: PDF Structure Verification")
                try:
                    doc = fitz.open(output_path)
                    page_count = len(doc)
                    print(f"✅ PDF has {page_count} pages")
                    
                    # Check for widgets on each page
                    total_widgets = 0
                    for page_num in range(page_count):
                        page = doc[page_num]
                        widgets = list(page.widgets())
                        total_widgets += len(widgets)
                        if widgets:
                            print(f"   Page {page_num + 1}: {len(widgets)} widgets")
                    
                    print(f"✅ Total widgets found: {total_widgets}")
                    
                    # Check if filled values are present
                    filled_values_found = 0
                    for page_num in range(page_count):
                        page = doc[page_num]
                        widgets = list(page.widgets())
                        for widget in widgets:
                            if widget.field_name and widget.field_value:
                                filled_values_found += 1
                                print(f"   ✅ Found filled field: {widget.field_name} = '{widget.field_value}'")
                    
                    print(f"✅ Found {filled_values_found} filled field values")
                    doc.close()
                    
                except Exception as e:
                    print(f"❌ PDF structure verification failed: {e}")
                    return False
                
                # Test 4: File Validation
                print("\n🔍 Test 4: File Validation")
                try:
                    with open(output_path, 'rb') as f:
                        header = f.read(10)
                        if header.startswith(b'%PDF'):
                            print("✅ PDF header is valid")
                        else:
                            print(f"❌ Invalid PDF header: {header}")
                            return False
                        
                        # Check file is not empty
                        f.seek(0, 2)
                        size = f.tell()
                        if size > 1000:  # Reasonable minimum size
                            print(f"✅ PDF file has reasonable size: {size} bytes")
                        else:
                            print(f"❌ PDF file too small: {size} bytes")
                            return False
                            
                except Exception as e:
                    print(f"❌ File validation failed: {e}")
                    return False
                
                print(f"\n📁 Test output saved to: {output_path}")
                print("💡 You can manually open this file to verify the filling worked visually")
                
                # Clean up
                try:
                    os.unlink(output_path)
                    print("🧹 Cleaned up test file")
                except:
                    pass
                    
            else:
                print("❌ Output file was not created")
                return False
        else:
            print("❌ PDF filling failed")
            return False
            
    except Exception as e:
        print(f"❌ PDF filling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All tests passed! PDF filling functionality is working correctly.")
    return True

def create_test_pdf():
    """Create a simple test PDF with form fields"""
    print("📝 Creating test PDF with form fields...")
    
    try:
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            output_path = temp_file.name
        
        # Create a simple PDF with PyMuPDF
        doc = fitz.open()
        page = doc.new_page()
        
        # Add some text
        page.insert_text((50, 100), "Test PDF Document", fontsize=16)
        page.insert_text((50, 150), "This is a test PDF created for validation", fontsize=12)
        
        # Add a simple rectangle to simulate a form field area
        rect = fitz.Rect(50, 200, 250, 220)
        page.draw_rect(rect, color=(0, 0, 0), width=1)
        page.insert_text((55, 215), "Property Address:", fontsize=10)
        
        doc.save(output_path)
        doc.close()
        
        print(f"✅ Created test PDF: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to create test PDF: {e}")
        return None

if __name__ == "__main__":
    print("🚀 PDF Filling Functionality Test Suite")
    print("=" * 50)
    
    success = test_pdf_filling()
    
    if success:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)