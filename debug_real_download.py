#!/usr/bin/env python3
"""
Debug the real download process step by step with maximum logging
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def debug_step_by_step():
    """Debug each step of the real download process"""
    
    print("🔍 DEBUGGING REAL DOWNLOAD PROCESS STEP BY STEP")
    print("=" * 60)
    
    try:
        from pdf_processor import PDFProcessor
        
        # Create the exact document structure that would come from the database
        document = {
            'id': 'debug_real_download',
            'name': 'Connecticut Home Energy Solutions Form',
            'file_path': os.path.join(os.path.dirname(__file__), 'homworks.pdf'),
            'user1_data': {
                'first_name': 'John',
                'last_name': 'Smith',
                'property_address': '123 Main Street'
            },
            'user2_data': {
                'applicant_signature': 'John Smith Real Signature',
                'owner_signature': 'Jane Owner Real Signature'
            }
        }
        
        processor = PDFProcessor()
        output_path = os.path.join(os.path.dirname(__file__), 'DEBUG_REAL_DOWNLOAD.pdf')
        
        print("📋 Step 1: Before processing - check source PDF")
        import fitz
        doc_check = fitz.open(document['file_path'])
        page_check = doc_check[2]
        widgets_check = list(page_check.widgets())
        
        sig_widgets_before = [w for w in widgets_check if w.field_name in ['signature3', 'property_ower_sig3']]
        print(f"Source PDF signature widgets:")
        for w in sig_widgets_before:
            print(f"  {w.field_name}: '{w.field_value}'")
        doc_check.close()
        
        print(f"\n📋 Step 2: Call fill_pdf_with_force_visible (the real download method)")
        
        # This is exactly what happens in the download
        success = processor.fill_pdf_with_force_visible(document['file_path'], document, output_path)
        
        if success:
            print(f"✅ fill_pdf_with_force_visible returned success")
            
            print(f"\n📋 Step 3: Check the output PDF immediately")
            doc_output = fitz.open(output_path)
            page_output = doc_output[2]
            widgets_output = list(page_output.widgets())
            
            sig_widgets_after = [w for w in widgets_output if w.field_name in ['signature3', 'property_ower_sig3']]
            print(f"Output PDF signature widgets:")
            for w in sig_widgets_after:
                print(f"  {w.field_name}: '{w.field_value}'")
                if w.field_value:
                    print(f"    ✅ HAS VALUE!")
                else:
                    print(f"    ❌ NO VALUE!")
            
            # Check ALL text fields to see what got filled
            print(f"\nAll text fields in output PDF:")
            text_widgets = [w for w in widgets_output if w.field_type == 7]  # Text fields
            for w in text_widgets:
                if w.field_value:
                    print(f"  ✅ {w.field_name}: '{w.field_value}'")
                else:
                    print(f"  ⭕ {w.field_name}: (empty)")
            
            doc_output.close()
            
            print(f"\n📋 Step 4: File info")
            file_size = os.path.getsize(output_path)
            print(f"Output file: {output_path}")
            print(f"File size: {file_size:,} bytes")
            
        else:
            print(f"❌ fill_pdf_with_force_visible returned failure")
            
        return success
        
    except Exception as e:
        print(f"❌ Error in step-by-step debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = debug_step_by_step()
    
    print(f"\n📊 DEBUG RESULTS:")
    print(f"   Real download debug: {'✅ COMPLETED' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n💡 KEY QUESTION:")
        print(f"   Do the signature widgets show values in the debug output above?")
        print(f"   If YES but PDF appears empty: PDF viewer issue")
        print(f"   If NO: Our processing is clearing the values")

if __name__ == "__main__":
    main()