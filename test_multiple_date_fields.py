#!/usr/bin/env python3
"""
Test to identify and fix multiple Date field issue
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def analyze_date_fields():
    """Analyze all Date fields in the PDF to identify them properly"""
    
    homeworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homeworks_path):
        try:
            from embedded_homworks import save_homworks_pdf_to_file
            save_homworks_pdf_to_file(homeworks_path)
        except ImportError:
            print(f"❌ Error: {homeworks_path} not found")
            return None
    
    print("🔍 Analyzing Date Fields in Connecticut Home Energy Solutions PDF")
    print("=" * 80)
    
    # Extract PDF fields
    processor = PDFProcessor()
    field_analysis = processor.extract_fields_with_pymupdf(homeworks_path)
    
    if "error" in field_analysis:
        print(f"❌ Error: {field_analysis['error']}")
        return None
    
    pdf_fields = field_analysis.get('fields', [])
    
    # Find all Date fields
    date_fields = []
    signature_fields = []
    
    for field in pdf_fields:
        field_name = field.get('name', '')
        field_type = field.get('type', '')
        position = field.get('position', {})
        page = field.get('page', 0)
        
        if 'Date' in field_name:
            date_fields.append({
                'name': field_name,
                'type': field_type,
                'page': page + 1,  # Convert to 1-indexed
                'x': position.get('x', 0),
                'y': position.get('y', 0),
                'context': f"Page {page + 1} at ({position.get('x', 0):.0f}, {position.get('y', 0):.0f})"
            })
        
        if 'Signature' in field_name:
            signature_fields.append({
                'name': field_name,
                'type': field_type,
                'page': page + 1,
                'x': position.get('x', 0),
                'y': position.get('y', 0),
                'context': f"Page {page + 1} at ({position.get('x', 0):.0f}, {position.get('y', 0):.0f})"
            })
    
    print(f"📋 Found {len(date_fields)} Date fields:")
    for i, field in enumerate(date_fields):
        print(f"   {i+1}. {field['name']} - {field['context']}")
        
        # Determine likely purpose based on position
        if field['y'] > 600:
            purpose = "Upper section (Property/Applicant info)"
        elif field['y'] > 450 and field['y'] <= 600:
            purpose = "Middle section (Authorization area)"
        elif field['y'] > 300 and field['y'] <= 450:
            purpose = "Lower middle (Qualification area)"
        else:
            purpose = "Lower section (Property owner area)"
        
        print(f"       Likely purpose: {purpose}")
    
    print(f"\n📋 Found {len(signature_fields)} Signature fields:")
    for i, field in enumerate(signature_fields):
        print(f"   {i+1}. {field['name']} - {field['context']}")
        
        # Determine likely purpose based on position
        if field['y'] > 450:
            purpose = "Applicant signature area"
        else:
            purpose = "Property owner signature area"
        
        print(f"       Likely purpose: {purpose}")
    
    return date_fields, signature_fields

def suggest_improved_mapping():
    """Suggest improved field mapping to handle multiple Date fields"""
    
    print(f"\n💡 Improved Field Mapping Strategy:")
    print("=" * 80)
    
    improved_mapping = {
        "Problem": "Multiple 'Date' fields with same name",
        "Solution": "Use position-based identification",
        "Implementation": [
            "1. Find all Date fields and sort by position",
            "2. Assign based on Y-coordinate (vertical position)",
            "3. Create context-aware field matching",
            "4. Use field index or position as tie-breaker"
        ]
    }
    
    print(f"🚨 Current Issue:")
    print(f"   • Multiple PDF fields named 'Date'")
    print(f"   • Exact name matching picks the first one found")
    print(f"   • May not be the intended field for authorization")
    
    print(f"\n🔧 Proposed Solution:")
    print(f"   • Map 'authorization_date' to Date field near Applicant Signature")
    print(f"   • Map 'owner_signature_date' to Date field near Property Owner Signature")
    print(f"   • Use position-based selection when field names are identical")
    
    print(f"\n📝 Implementation Options:")
    print(f"   Option A: Use field position to distinguish Date fields")
    print(f"   Option B: Check proximity to signature fields")
    print(f"   Option C: Use page + position combination for unique identification")
    
    return improved_mapping

def create_position_based_mapping():
    """Create position-based field mapping for ambiguous fields"""
    
    print(f"\n🎯 Position-Based Field Mapping:")
    print("=" * 80)
    
    position_mapping = '''
def map_form_data_with_position_awareness(form_data, pdf_fields):
    """Enhanced mapping that handles multiple fields with same name"""
    
    # Sort Date fields by position to assign them correctly
    date_fields = [f for f in pdf_fields if f['name'] == 'Date']
    date_fields.sort(key=lambda f: f['position']['y'])  # Sort by Y position
    
    # Map authorization_date to Date field near Applicant Signature (middle area)
    for field in date_fields:
        if 450 <= field['position']['y'] <= 500:  # Authorization area
            if form_data.get('authorization_date'):
                field['value'] = form_data['authorization_date']
                field['assigned_to'] = 'user2'
                print(f"✅ Mapped authorization_date to Date field at ({field['position']['x']}, {field['position']['y']})")
                break
    
    # Map owner_signature_date to Date field near Property Owner Signature (lower area)
    for field in date_fields:
        if field['position']['y'] > 600:  # Property owner area
            if form_data.get('owner_signature_date'):
                field['value'] = form_data['owner_signature_date']
                field['assigned_to'] = 'user2'
                print(f"✅ Mapped owner_signature_date to Date field at ({field['position']['x']}, {field['position']['y']})")
                break
'''
    
    print(position_mapping)
    return position_mapping

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Multiple Date Fields Analysis")
    print("Investigating Section 3 Applicant Signature and Date field issues")
    print()
    
    # Analyze the fields
    result = analyze_date_fields()
    
    if result:
        date_fields, signature_fields = result
        
        # Suggest improvements
        suggest_improved_mapping()
        create_position_based_mapping()
        
        print(f"\n🎯 Recommended Action:")
        print(f"   1. Update field mapping to use position-based selection")
        print(f"   2. Map authorization_date to Date field near Applicant Signature")
        print(f"   3. Map owner_signature_date to Date field near Property Owner Signature")
        print(f"   4. Test with real form data to verify correct placement")
        
        print(f"\n📍 Field Positions Found:")
        print(f"   • Date fields: {len(date_fields)} total")
        print(f"   • Signature fields: {len(signature_fields)} total")
        print(f"   • Need position-aware mapping for disambiguation")
    else:
        print(f"\n❌ Could not analyze PDF fields")

if __name__ == "__main__":
    main()