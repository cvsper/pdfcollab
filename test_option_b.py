#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_b_complete():
    """Test filling Option B assistance programs"""
    
    # Sample form data with Option B programs selected
    form_data = {
        # Section 1: Property Information
        'property_address1': '123 Main Street',
        'apt_num1': '2B',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02101',
        'num_of_apt1': '1',
        'phone_num1': '617-555-0123',
        
        # Section 2: Personal Information
        'first_name2': 'Alice',
        'last_name2': 'Johnson',
        'phone2': '617-555-0100',
        'email2': 'alice.johnson@email.com',
        
        # Section 2: Dwelling Type - Apartment
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'Yes',
        'dwelling_condo1': 'No',
        
        # Section 2: Heating Fuel - Electric
        'fuel_type_elec2': 'Yes',
        'fuel_type_gas2': 'No',
        'fuel_type_oil2': 'No',
        'fuel_type_propane2': 'No',
        
        # Section 2: Applicant Type - Renter
        'owner2': 'No',
        'renter2': 'Yes',
        
        # Section 2: Electric Utility - Eversource
        'electric_eversource2': 'Yes',
        'electric_ui2': 'No',
        
        # Section 2: Account Information
        'elect_acct_applicant2': 'Yes',
        'elect_acct_other2': 'No',
        'elec_acct_num2': '1234567890',
        
        # Section 4: Option A Assistance Programs - ALL UNCHECKED
        'elec_discount4': 'No',
        'low_income4': 'No',
        'matching_payment_eversource4': 'No',
        'bill_forgive4': 'No',
        'matching_pay_united4': 'No',
        
        # Section 4: Option B Assistance Programs - ALL CHECKED
        'ebt4': 'Yes',
        'energy_award_letter4': 'Yes',
        'section_eight4': 'Yes',
        
        # Section 4: Option D - UNCHECKED
        'multifam4': 'No',
        
        # Section 4: Income Information
        'people_in_household4': '2',
        'annual_income4': '45000',
        
        # Section 4: Landlord Information (for renters)
        'landlord_name3': 'John Smith',
        'address3': '456 Property Lane',
        'city3': 'Boston',
        'text_55cits': 'MA',
        'text_56qpfj': '02102',
        'phone3': '617-555-0200',
        'email3': 'landlord@properties.com'
    }
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Load the template PDF
    template_path = "homworks.pdf"
    if not os.path.exists(template_path):
        print(f"❌ Template PDF not found: {template_path}")
        return
    
    # Fill the form
    try:
        output_path = "OPTION_B_COMPLETE_TEST.pdf"
        
        print("🔄 Processing Option B assistance programs...")
        print("✅ Option B programs to be checked:")
        print("   - EBT (Food Stamps)")
        print("   - Energy Award Letter") 
        print("   - Section Eight")
        print("❌ Option A programs (unchecked)")
        print("❌ Option D programs (unchecked)")
        
        # Create document structure matching the expected format
        document = {
            'user1_data': form_data,
            'user2_data': {}
        }
        
        success = processor.fill_pdf_with_pymupdf(template_path, document, output_path)
        
        if success:
            print(f"✅ Option B test PDF created successfully: {output_path}")
            print(f"📂 File location: {os.path.abspath(output_path)}")
            
            # Add dwelling type visual indicators - for apartments
            document_with_dwelling = {
                'user1_data': {**form_data, 'dwelling_type': 'apartment'}
            }
            
            # Re-open PDF to add visual indicators
            import fitz
            doc = fitz.open(output_path)
            processor.add_dwelling_visual_indicators(doc, document_with_dwelling)
            temp_path = output_path + "_temp"
            doc.save(temp_path)
            doc.close()
            
            # Replace original with updated version
            import shutil
            shutil.move(temp_path, output_path)
            print("✅ Visual dwelling indicators added")
            
        else:
            print("❌ Failed to create Option B test PDF")
            
    except Exception as e:
        print(f"❌ Error creating Option B test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_option_b_complete()