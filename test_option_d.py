#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor

def test_option_d_complete():
    """Test filling Option D assistance program"""
    
    # Sample form data with Option D program selected
    form_data = {
        # Section 1: Property Information
        'property_address1': '789 Oak Avenue',
        'apt_num1': '5A',
        'city1': 'Boston',
        'state1': 'MA',
        'zip1': '02103',
        'num_of_apt1': '1',
        'phone_num1': '617-555-0789',
        
        # Section 2: Personal Information
        'first_name2': 'David',
        'last_name2': 'Wilson',
        'phone2': '617-555-0400',
        'email2': 'david.wilson@email.com',
        
        # Section 2: Dwelling Type - Condominium
        'dwelling_single_fam1': 'No',
        'dwelling_apt1': 'No',
        'dwelling_condo1': 'Yes',
        
        # Section 2: Heating Fuel - Gas
        'fuel_type_elec2': 'No',
        'fuel_type_gas2': 'Yes',
        'fuel_type_oil2': 'No',
        'fuel_type_propane2': 'No',
        
        # Section 2: Applicant Type - Property Owner
        'owner2': 'Yes',
        'renter2': 'No',
        
        # Section 2: Electric Utility - UI
        'electric_eversource2': 'No',
        'electric_ui2': 'Yes',
        
        # Section 2: Gas Utility - Eversource
        'gas_util_cng2': 'No',
        'gas_util_eversource2': 'Yes',
        'gas_util_scg2': 'No',
        
        # Section 2: Account Information
        'elect_acct_applicant2': 'Yes',
        'elect_acct_other2': 'No',
        'gas_acct_applicant2': 'Yes',
        'gas_acct_other2': 'No',
        'elec_acct_num2': '9876543210',
        'gas_acct_num2': '5432109876',
        
        # Section 4: Option A Assistance Programs - ALL UNCHECKED
        'elec_discount4': 'No',
        'low_income4': 'No',
        'matching_payment_eversource4': 'No',
        'bill_forgive4': 'No',
        'matching_pay_united4': 'No',
        
        # Section 4: Option B Assistance Programs - ALL UNCHECKED
        'ebt4': 'No',
        'energy_award_letter4': 'No',
        'section_eight4': 'No',
        
        # Section 4: Option D - CHECKED
        'multifam4': 'Yes',
        
        # Section 4: Income Information
        'people_in_household4': '3',
        'annual_income4': '75000'
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
        output_path = "OPTION_D_COMPLETE_TEST.pdf"
        
        print("🔄 Processing Option D assistance program...")
        print("✅ Option D program to be checked:")
        print("   - Multifam4 (Multi-family building assistance)")
        print("❌ Option A programs (unchecked)")
        print("❌ Option B programs (unchecked)")
        
        # Create document structure matching the expected format
        document = {
            'user1_data': form_data,
            'user2_data': {}
        }
        
        success = processor.fill_pdf_with_pymupdf(template_path, document, output_path)
        
        if success:
            print(f"✅ Option D test PDF created successfully: {output_path}")
            print(f"📂 File location: {os.path.abspath(output_path)}")
            
            # Add dwelling type visual indicators - for condominium
            document_with_dwelling = {
                'user1_data': {**form_data, 'dwelling_type': 'condominium'}
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
            print("❌ Failed to create Option D test PDF")
            
    except Exception as e:
        print(f"❌ Error creating Option D test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_option_d_complete()