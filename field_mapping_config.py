#!/usr/bin/env python3
"""
Explicit field mapping configuration for Connecticut Home Energy Solutions PDF
This ensures each form field is mapped to the correct PDF field location
"""

# Exact field mappings based on PDF analysis
# Format: 'form_field_name': {'pdf_field_name': 'exact_name', 'page': page_number, 'type': 'field_type'}

FIELD_MAPPING_CONFIG = {
    # Section 1: Property Information (Page 3)
    'property_address': {
        'pdf_field_name': 'Property Address',
        'page': 2,  # 0-indexed (page 3)
        'type': 'text',
        'position': {'x': 37.0, 'y': 156.0}
    },
    'apartment_number': {
        'pdf_field_name': 'Apartment Number',
        'page': 2,
        'type': 'text',
        'position': {'x': 233.0, 'y': 156.0}
    },
    'city': {
        'pdf_field_name': 'City',
        'page': 2,
        'type': 'text',
        'position': {'x': 36.0, 'y': 182.0}
    },
    'state': {
        'pdf_field_name': 'State',
        'page': 2,
        'type': 'text',
        'position': {'x': 184.0, 'y': 182.0}
    },
    'zip_code': {
        'pdf_field_name': 'ZIP Code',
        'page': 2,
        'type': 'text',
        'position': {'x': 233.0, 'y': 182.0}
    },
    'apartments_count': {
        'pdf_field_name': 'Num Of Apt1',
        'page': 2,
        'type': 'text',
        'position': {'x': 185.0, 'y': 210.0}
    },
    
    # Section 2: Applicant Information (Page 3)
    'first_name': {
        'pdf_field_name': 'First Name',
        'page': 2,
        'type': 'text',
        'position': {'x': 314.0, 'y': 168.0}
    },
    'last_name': {
        'pdf_field_name': 'Last Name',
        'page': 2,
        'type': 'text',
        'position': {'x': 439.0, 'y': 169.0}
    },
    'telephone': {
        'pdf_field_name': 'Phone Number',
        'page': 2,
        'type': 'text',
        'position': {'x': 313.0, 'y': 195.0}
    },
    'email': {
        'pdf_field_name': 'Email Address',
        'page': 2,
        'type': 'text',
        'position': {'x': 439.0, 'y': 196.0}
    },
    
    # Dwelling Type (Page 3)
    'dwelling_type_single_family': {
        'pdf_field_name': 'Single Family Home (Checkbox)',
        'page': 2,
        'type': 'checkbox',
        'position': {'x': 40.0, 'y': 256.0}
    },
    'dwelling_type_apartment': {
        'pdf_field_name': 'Apartment (Checkbox)',
        'page': 2,
        'type': 'checkbox',
        'position': {'x': 41.0, 'y': 268.0}
    },
    'dwelling_type_condominium': {
        'pdf_field_name': 'Condominium (Checkbox)',
        'page': 2,
        'type': 'checkbox',
        'position': {'x': 41.0, 'y': 280.0}
    },
    
    # Heating Fuel Type (Page 3)
    'heating_fuel_electric': {
        'pdf_field_name': 'Electric Heat (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 317.0, 'y': 235.0}
    },
    'heating_fuel_gas': {
        'pdf_field_name': 'Gas Heat (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 353.0, 'y': 235.0}
    },
    'heating_fuel_oil': {
        'pdf_field_name': 'Oil Heat (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 316.0, 'y': 247.0}
    },
    'heating_fuel_propane': {
        'pdf_field_name': 'Propane Heat (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 353.0, 'y': 247.0}
    },
    
    # Applicant Type (Page 3)
    'applicant_type_owner': {
        'pdf_field_name': 'Property Owner (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 442.0, 'y': 235.0}
    },
    'applicant_type_renter': {
        'pdf_field_name': 'Renter (Radio Button)',
        'page': 2,
        'type': 'radio',
        'position': {'x': 442.0, 'y': 247.0}
    },
    
    # Utility Information (Page 3)
    'electric_account': {
        'pdf_field_name': 'Elec Acct Num2',
        'page': 2,
        'type': 'text',
        'position': {'x': 312.0, 'y': 363.0}
    },
    'gas_account': {
        'pdf_field_name': 'Gas Acct Num2',
        'page': 2,
        'type': 'text',
        'position': {'x': 440.0, 'y': 363.0}
    },
    
    # Section 3: Qualification (Page 4)
    'household_size': {
        'pdf_field_name': 'People In Household4',
        'page': 3,  # 0-indexed (page 4)
        'type': 'text',
        'position': {'x': 312.0, 'y': 216.0}
    },
    'adults_count': {
        'pdf_field_name': 'People In Household Overage4',
        'page': 3,
        'type': 'text',
        'position': {'x': 312.0, 'y': 244.0}
    },
    'annual_income': {
        'pdf_field_name': 'Annual Income4',
        'page': 3,
        'type': 'text',
        'position': {'x': 312.0, 'y': 273.0}
    },
    
    # Section 4: Authorization (Page 3) - USER 2 FIELDS
    'applicant_signature': {
        'pdf_field_name': 'Applicant Signature',
        'page': 2,
        'type': 'signature',
        'position': {'x': 43.0, 'y': 470.0},
        'assigned_to': 'user2'
    },
    'authorization_date': {
        'pdf_field_name': 'Date',
        'page': 2,
        'type': 'text',
        'position': {'x': 441.0, 'y': 471.0},
        'assigned_to': 'user2'
    },
    
    # Property Owner Information (Page 3)
    'owner_name': {
        'pdf_field_name': 'Landlord Name3',
        'page': 2,
        'type': 'text',
        'position': {'x': 37.0, 'y': 549.0}
    },
    'owner_address': {
        'pdf_field_name': 'Address3',
        'page': 2,
        'type': 'text',
        'position': {'x': 36.0, 'y': 575.0}
    },
    'owner_telephone': {
        'pdf_field_name': 'Phone Number',
        'page': 2,
        'type': 'text',
        'position': {'x': 36.0, 'y': 629.0}
    },
    'owner_email': {
        'pdf_field_name': 'Email Address',
        'page': 2,
        'type': 'text',
        'position': {'x': 36.0, 'y': 655.0}
    },
    'owner_signature': {
        'pdf_field_name': 'Property Owner Signature',
        'page': 2,
        'type': 'signature',
        'position': {'x': 319.0, 'y': 612.0},
        'assigned_to': 'user2'
    },
    'owner_signature_date': {
        'pdf_field_name': 'Date',
        'page': 2,
        'type': 'text',
        'position': {'x': 321.0, 'y': 643.0},
        'assigned_to': 'user2'
    }
}

# Section 5 fields are handled separately with exact positions
# These are added via PyMuPDF text annotations on page 5
SECTION5_EXACT_POSITIONS = {
    'account_holder_name_affidavit': {
        'page': 4,  # 0-indexed (page 5)
        'x': 155, 'y': 145, 'width': 250, 'height': 25,
        'assigned_to': 'user2'
    },
    'household_member_names_no_income': {
        'page': 4,
        'x': 45, 'y': 265, 'width': 450, 'height': 80,
        'assigned_to': 'user2'
    },
    'affidavit_signature': {
        'page': 4,
        'x': 40, 'y': 490, 'width': 200, 'height': 30,
        'assigned_to': 'user2'
    },
    'printed_name_affidavit': {
        'page': 4,
        'x': 315, 'y': 490, 'width': 230, 'height': 25,
        'assigned_to': 'user2'
    },
    'date_affidavit': {
        'page': 4,
        'x': 50, 'y': 535, 'width': 150, 'height': 25,
        'assigned_to': 'user2'
    },
    'telephone_affidavit': {
        'page': 4,
        'x': 315, 'y': 535, 'width': 150, 'height': 25,
        'assigned_to': 'user2'
    }
}

def get_pdf_field_for_form_field(form_field_name):
    """Get the exact PDF field mapping for a form field"""
    
    # Check regular field mappings
    if form_field_name in FIELD_MAPPING_CONFIG:
        return FIELD_MAPPING_CONFIG[form_field_name]
    
    # Check Section 5 mappings
    if form_field_name in SECTION5_EXACT_POSITIONS:
        return {
            'pdf_field_name': form_field_name,
            'page': SECTION5_EXACT_POSITIONS[form_field_name]['page'],
            'type': 'text',
            'position': {
                'x': SECTION5_EXACT_POSITIONS[form_field_name]['x'],
                'y': SECTION5_EXACT_POSITIONS[form_field_name]['y']
            },
            'assigned_to': SECTION5_EXACT_POSITIONS[form_field_name]['assigned_to']
        }
    
    return None

def validate_field_mappings():
    """Validate that all required fields have mappings"""
    required_fields = [
        # Section 1
        'property_address', 'apartment_number', 'city', 'state', 'zip_code',
        # Section 2
        'first_name', 'last_name', 'telephone', 'email',
        # Section 3
        'household_size', 'adults_count', 'annual_income',
        # Section 4
        'applicant_signature', 'authorization_date',
        # Section 5
        'account_holder_name_affidavit', 'affidavit_signature'
    ]
    
    missing = []
    for field in required_fields:
        if not get_pdf_field_for_form_field(field):
            missing.append(field)
    
    if missing:
        print(f"⚠️  Missing mappings for: {', '.join(missing)}")
        return False
    
    print("✅ All required fields have mappings")
    return True

if __name__ == "__main__":
    print("Connecticut Home Energy Solutions - Field Mapping Configuration")
    print("=" * 60)
    print(f"Regular field mappings: {len(FIELD_MAPPING_CONFIG)}")
    print(f"Section 5 field mappings: {len(SECTION5_EXACT_POSITIONS)}")
    print(f"Total mappings: {len(FIELD_MAPPING_CONFIG) + len(SECTION5_EXACT_POSITIONS)}")
    print()
    validate_field_mappings()