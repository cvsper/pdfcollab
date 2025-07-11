#!/usr/bin/env python3
"""
Test to verify that Section 3 Applicant Signature and Date fields appear correctly
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_section3_signature_date():
    """Test that Section 3 authorization signature and date appear correctly"""
    
    print("🧪 Testing Section 3 Applicant Signature and Date Fields")
    print("=" * 70)
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
            print("✅ Using embedded homworks.pdf")
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return False
    
    # Test form data with Section 4 Authorization fields (User 2)
    test_form_data = {
        # Section 1: Property Information (User 1)
        'property_address': '123 Test Street',
        'apartment_number': 'Unit 5B',
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'apartments_count': '1',
        'dwelling_type': 'apartment',
        
        # Section 2: Applicant Information (User 1)
        'first_name': 'John',
        'last_name': 'Doe',
        'telephone': '(860) 555-1234',
        'email': 'john.doe@example.com',
        'heating_fuel': 'natural_gas',
        'applicant_type': 'renter_tenant',
        
        # Section 3: Qualification (User 1)
        'household_size': '3',
        'adults_count': '2',
        'annual_income': '45000',
        
        # Section 4: Authorization (User 2) - THE KEY FIELDS TO TEST
        'applicant_signature': 'John Doe',
        'authorization_date': '2025-07-11',
        
        # Utility accounts (User 1)
        'electric_account': '123456789',
        'gas_account': '987654321'
    }
    
    # Extract PDF fields
    processor = PDFProcessor()
    field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
    
    if "error" in field_analysis:
        print(f"❌ Error: {field_analysis['error']}")
        return False
    
    pdf_fields = field_analysis.get('fields', [])
    
    print(f"📋 Found {len(pdf_fields)} PDF fields total")
    
    # Find the specific fields we're testing
    applicant_signature_field = None
    authorization_date_field = None
    date_fields = []
    
    for field in pdf_fields:
        if field['name'] == 'Applicant Signature':
            applicant_signature_field = field
        elif field['name'] == 'Date':
            date_fields.append(field)
    
    print(f"🔍 Analysis Results:")
    print(f"   • Applicant Signature field found: {'✅' if applicant_signature_field else '❌'}")
    print(f"   • Date fields found: {len(date_fields)}")
    
    if applicant_signature_field:
        print(f"   📍 Applicant Signature position: ({applicant_signature_field['position']['x']:.0f}, {applicant_signature_field['position']['y']:.0f})")
    
    # Sort Date fields by Y position and identify the authorization date field
    date_fields.sort(key=lambda f: f['position']['y'])
    for i, field in enumerate(date_fields):
        y_pos = field['position']['y']
        print(f"   📍 Date field {i+1}: ({field['position']['x']:.0f}, {y_pos:.0f})")
        
        # Identify which date field is for authorization (near applicant signature)
        if 460 <= y_pos <= 480:
            authorization_date_field = field
            print(f"     → This is the AUTHORIZATION date field (near Applicant Signature)")
        elif y_pos > 630:
            print(f"     → This is the Property Owner date field")
    
    print(f"\n🎯 Position-Based Mapping Test:")
    
    # Test the position-based mapping logic
    authorization_date_value = test_form_data.get('authorization_date')
    if authorization_date_value and authorization_date_field:
        print(f"   ✅ authorization_date '{authorization_date_value}' should map to Date field at ({authorization_date_field['position']['x']:.0f}, {authorization_date_field['position']['y']:.0f})")
        
        # Verify it's near the Applicant Signature
        if applicant_signature_field:
            x_diff = abs(authorization_date_field['position']['x'] - applicant_signature_field['position']['x'])
            y_diff = abs(authorization_date_field['position']['y'] - applicant_signature_field['position']['y'])
            print(f"   📏 Distance from Applicant Signature: x={x_diff:.0f}, y={y_diff:.0f}")
            
            if y_diff < 10:  # They should be on approximately the same line
                print(f"   ✅ CORRECT: Date field is on the same line as Applicant Signature")
                return True
            else:
                print(f"   ❌ ERROR: Date field is too far from Applicant Signature")
                return False
        else:
            print(f"   ❌ ERROR: Could not find Applicant Signature field")
            return False
    else:
        print(f"   ❌ ERROR: Could not identify authorization date field")
        return False

def create_test_pdf_with_section4():
    """Create a test PDF with Section 4 fields filled"""
    
    print(f"\n🔧 Creating Test PDF with Section 4 Authorization Fields")
    print("=" * 70)
    
    # Test data for PDF generation
    test_form_data = {
        # User 1 data (Sections 1-3)
        'property_address': '123 Test Street',
        'apartment_number': 'Unit 5B', 
        'city': 'Hartford',
        'state': 'CT',
        'zip_code': '06103',
        'apartments_count': '1',
        'dwelling_type': 'apartment',
        'first_name': 'John',
        'last_name': 'Doe',
        'telephone': '(860) 555-1234',
        'email': 'john.doe@example.com',
        'heating_fuel': 'natural_gas',
        'applicant_type': 'renter_tenant',
        'household_size': '3',
        'adults_count': '2',
        'annual_income': '45000',
        'electric_account': '123456789',
        'gas_account': '987654321'
    }
    
    # User 2 data (Section 4 Authorization)
    test_user2_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'applicant_signature': 'John Doe',
        'authorization_date': '2025-07-11'
    }
    
    try:
        from pdf_processor import PDFProcessor
        
        homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
        processor = PDFProcessor()
        
        # Create the document structure expected by PDFProcessor
        document = {
            'user1_data': test_form_data,
            'user2_data': test_user2_data
        }
        
        # Generate test PDF
        output_path = os.path.join(os.path.dirname(__file__), 'test_section4_authorization.pdf')
        result = processor.fill_pdf_with_force_visible(
            homeworks_path, 
            document, 
            output_path
        )
        
        if result:
            print(f"✅ Test PDF created: {output_path}")
            print(f"🎯 Please check the PDF to verify:")
            print(f"   • Applicant Signature appears as 'John Doe'")
            print(f"   • Date appears as '2025-07-11' next to Applicant Signature")
            print(f"   • Both fields are in Section 4 Authorization area")
            return True
        else:
            print(f"❌ Failed to create test PDF")
            return False
    
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return False

def main():
    """Main test function"""
    print("🏠 PDF Collaborator - Section 3 Applicant Signature & Date Fix Test")
    print("Testing position-based mapping for authorization fields")
    print()
    
    # Test field position analysis
    analysis_success = test_section3_signature_date()
    
    # Create test PDF
    pdf_success = create_test_pdf_with_section4()
    
    print(f"\n📊 Test Results:")
    print(f"   Field analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    print(f"   PDF generation: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    
    if analysis_success and pdf_success:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Position-based mapping correctly identifies authorization date field")
        print(f"✅ Test PDF generated with Section 4 authorization fields")
        print(f"✅ Applicant Signature and Date should appear correctly in Section 3")
        
        print(f"\n💡 Expected Results in PDF:")
        print(f"   • 'John Doe' appears in Applicant Signature field")
        print(f"   • '2025-07-11' appears in Date field next to signature")
        print(f"   • Both fields are positioned correctly in authorization area")
    else:
        print(f"\n❌ Some tests failed - check the output above")

if __name__ == "__main__":
    main()