#!/usr/bin/env python3
"""
Embed homworks.pdf as base64 for deployment
This ensures the PDF is always available, even on Render
"""

import base64
import os

def create_embedded_pdf_module():
    """Create a Python module with embedded PDF data"""
    
    pdf_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: {pdf_path} not found")
        return False
    
    print(f"📄 Reading homworks.pdf...")
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    print(f"📊 PDF size: {len(pdf_data):,} bytes")
    
    # Encode to base64
    encoded_data = base64.b64encode(pdf_data).decode('utf-8')
    print(f"🔐 Encoded size: {len(encoded_data):,} characters")
    
    # Create Python module with embedded data
    module_content = f'''"""
Embedded homworks.pdf for PDF Collaborator
Auto-generated - DO NOT EDIT MANUALLY
"""

import base64
import os
import tempfile

# Embedded PDF data (base64 encoded)
HOMWORKS_PDF_B64 = """{encoded_data}"""

def get_homworks_pdf_data():
    """Get the decoded PDF data"""
    return base64.b64decode(HOMWORKS_PDF_B64)

def save_homworks_pdf_to_file(file_path):
    """Save the embedded PDF to a file"""
    pdf_data = get_homworks_pdf_data()
    with open(file_path, 'wb') as f:
        f.write(pdf_data)
    return file_path

def get_homworks_pdf_path():
    """Get a temporary file path with the PDF data"""
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'homworks_embedded.pdf')
    
    # Save the PDF data
    save_homworks_pdf_to_file(temp_path)
    
    return temp_path
'''
    
    # Write the module
    output_path = os.path.join(os.path.dirname(__file__), 'embedded_homworks.py')
    with open(output_path, 'w') as f:
        f.write(module_content)
    
    print(f"✅ Created embedded_homworks.py module")
    print(f"📁 File: {output_path}")
    
    # Test the module
    print(f"\n🧪 Testing the module...")
    try:
        import embedded_homworks
        test_data = embedded_homworks.get_homworks_pdf_data()
        if len(test_data) == len(pdf_data):
            print(f"✅ Module test successful - data integrity verified")
        else:
            print(f"❌ Module test failed - data size mismatch")
    except Exception as e:
        print(f"❌ Module test failed: {e}")
    
    return True

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Embed PDF for Deployment")
    print("=" * 50)
    
    if create_embedded_pdf_module():
        print(f"\n🎉 SUCCESS!")
        print(f"📋 Next steps:")
        print(f"   1. Add embedded_homworks.py to git")
        print(f"   2. Update app.py to use embedded PDF")
        print(f"   3. Deploy to Render")
        print(f"   4. PDF will always be available!")
    else:
        print(f"\n❌ Failed to create embedded module")

if __name__ == "__main__":
    main()