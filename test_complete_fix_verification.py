#!/usr/bin/env python3
"""
Complete test verification - signatures, dates, and Section 4 fields all working together
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_complete_fix():
    """Test all fixes together: signatures, dates, and Section 4 fields"""
    
    print("🧪 COMPLETE FIX VERIFICATION TEST")
    print("=" * 50)
    
    # Create comprehensive test document
    test_document = {
        'id': 'complete_test',
        'name': 'complete_test.pdf',
        'pdf_fields': [
            # User 1 fields
            {
                'id': 'test_property_address',
                'name': 'Property Address',
                'value': '123 Test Street',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # Option A - Utility Programs
            {
                'id': 'test_elec_discount',
                'name': 'Elec Discount4 (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_low_income',
                'name': 'Low Income Program (Checkbox)',
                'value': 'true',
                'type': 'checkbox',
                'assigned_to': 'user1'
            },
            
            # Section 3 fields
            {
                'id': 'test_household_size',
                'name': 'People In Household4',
                'value': '4',
                'type': 'text',
                'assigned_to': 'user1'
            },
            {
                'id': 'test_annual_income',
                'name': 'Annual Income4',
                'value': '45000',
                'type': 'text',
                'assigned_to': 'user1'
            },
            
            # User 2 signatures
            {
                'id': 'test_signature1',
                'name': 'Applicant Signature',
                'value': 'John Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 440}
            },
            {
                'id': 'test_signature2',
                'name': 'Property Owner Signature',
                'value': 'Jane Smith',
                'type': 'signature',
                'assigned_to': 'user2',
                'position': {'x': 43, 'y': 612}
            },
            
            # User 2 dates
            {
                'id': 'test_auth_date',
                'name': 'Date',
                'value': '2025-07-11',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 200, 'y': 471.0}  # Near Applicant Signature
            },
            {
                'id': 'test_owner_date',
                'name': 'Date',
                'value': '2025-07-11',
                'type': 'text',
                'assigned_to': 'user2',
                'position': {'x': 200, 'y': 643.0}  # Near Property Owner Signature
            }
        ]
    }
    
    # Test the PDF processor
    processor = PDFProcessor()
    
    # Test with homworks.pdf
    input_pdf = 'homworks.pdf'
    output_pdf = 'COMPLETE_FIX_VERIFICATION.pdf'
    
    if not os.path.exists(input_pdf):
        print(f"❌ {input_pdf} not found")
        return False
    
    print(f"📄 Input PDF: {input_pdf}")
    print(f"📄 Output PDF: {output_pdf}")
    
    # Fill the PDF
    success = processor.fill_pdf_with_pymupdf(input_pdf, test_document, output_pdf)
    
    if success:
        print(f"\n✅ PDF filled successfully: {output_pdf}")
        
        # Verify all field types
        print("\n🔍 Verifying all field types in output PDF...")
        
        import fitz
        doc = fitz.open(output_pdf)
        
        verification_results = {
            'signatures': [],
            'dates': [],
            'section4': [],
            'user1_fields': []
        }
        
        # Check signatures, dates, and property address on page 3
        page3 = doc[2]
        widgets3 = list(page3.widgets())
        for widget in widgets3:
            field_name = widget.field_name
            field_value = widget.field_value
            
            if field_value and str(field_value) not in ['', 'False', 'Off']:
                if 'signature' in field_name.lower() or 'sig' in field_name.lower():
                    verification_results['signatures'].append(f"{field_name}: '{field_value}'")
                elif 'date' in field_name.lower():
                    verification_results['dates'].append(f"{field_name}: '{field_value}'")
                elif 'property_address' in field_name.lower():
                    verification_results['user1_fields'].append(f"{field_name}: '{field_value}'")
        
        # Check Section 4 fields on page 4
        page4 = doc[3]
        widgets4 = list(page4.widgets())
        for widget in widgets4:
            field_name = widget.field_name
            field_value = widget.field_value
            
            if field_value and str(field_value) not in ['', 'False', 'Off']:
                if any(field in field_name for field in ['elec_discount4', 'low_income4', 'people_in_household4', 'annual_income4']):
                    verification_results['section4'].append(f"{field_name}: '{field_value}'")
        
        
        doc.close()
        
        # Report results
        print("\n📊 VERIFICATION RESULTS:")
        print(f"   🖋️  Signatures filled: {len(verification_results['signatures'])}")
        for sig in verification_results['signatures']:
            print(f"      ✅ {sig}")
        
        print(f"   📅 Dates filled: {len(verification_results['dates'])}")
        for date in verification_results['dates']:
            print(f"      ✅ {date}")
        
        print(f"   📋 Section 4 fields filled: {len(verification_results['section4'])}")
        for s4 in verification_results['section4']:
            print(f"      ✅ {s4}")
        
        print(f"   👤 User 1 fields filled: {len(verification_results['user1_fields'])}")
        for u1 in verification_results['user1_fields']:
            print(f"      ✅ {u1}")
        
        # Success criteria
        signatures_ok = len(verification_results['signatures']) >= 2
        dates_ok = len(verification_results['dates']) >= 2
        section4_ok = len(verification_results['section4']) >= 3
        user1_ok = len(verification_results['user1_fields']) >= 1
        
        if signatures_ok and dates_ok and section4_ok and user1_ok:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print("✅ All fixes are working:")
            print("   ✅ Signatures appear on PDF")
            print("   ✅ Dates appear on PDF") 
            print("   ✅ Section 4 fields appear on PDF")
            print("   ✅ User 1 fields appear on PDF")
            return True
        else:
            print(f"\n⚠️  Some issues found:")
            if not signatures_ok:
                print("   ❌ Signatures not properly filled")
            if not dates_ok:
                print("   ❌ Dates not properly filled")
            if not section4_ok:
                print("   ❌ Section 4 not properly filled")
            if not user1_ok:
                print("   ❌ User 1 fields not properly filled")
            return False
    else:
        print("❌ PDF filling failed")
        return False

if __name__ == "__main__":
    success = test_complete_fix()
    if success:
        print("\n🎯 COMPLETE FIX VERIFICATION PASSED!")
        print("🚀 All user issues have been resolved!")
    else:
        print("\n❌ Some fixes still need work")