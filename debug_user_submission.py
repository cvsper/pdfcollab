#!/usr/bin/env python3
"""
Debug what happens during an actual user submission
Add this debugging code to the app to see what's happening
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

def debug_user_form_data():
    """Show what we should look for in user form data"""
    
    print("🐛 USER FORM DATA DEBUGGING GUIDE")
    print("=" * 50)
    
    print("🔍 Add this debugging code to app.py in the User 1 form submission section:")
    print()
    
    debug_code = '''
# ADD THIS DEBUGGING CODE AFTER LINE ~1325 in app.py (after collecting form data)

print("🐛 DEBUG: User 1 form data received:")
print(f"   qualification_option: {user1_data.get('qualification_option', 'NOT SET')}")
print(f"   utility_program: {user1_data.get('utility_program', 'NOT SET')}")
print(f"   documentation: {user1_data.get('documentation', 'NOT SET')}")

# Check if qualification fields are being received at all
form_keys = list(request.form.keys())
qualification_keys = [k for k in form_keys if 'qualification' in k or 'utility' in k or 'documentation' in k]
print(f"   Form keys related to qualification: {qualification_keys}")

# Show all form data for debugging
print("   All form data received:")
for key, value in request.form.items():
    if 'qualification' in key or 'utility' in key or 'documentation' in key or 'option' in key:
        print(f"      {key}: {value}")

print("   All form lists received:")
for key in request.form.keys():
    if 'qualification' in key or 'utility' in key or 'documentation' in key:
        list_values = request.form.getlist(key)
        if list_values:
            print(f"      {key} (list): {list_values}")
'''
    
    print(debug_code)
    print()
    
    print("🔍 Also add this debugging code in the qualification processing section (around line ~1607):")
    print()
    
    debug_code2 = '''
# ADD THIS BEFORE THE QUALIFICATION PROCESSING (around line 1607)

print("\\n🐛 DEBUG: About to process qualification options...")
print(f"   form_data keys: {list(form_data.keys())}")
print(f"   qualification_option value: '{form_data.get('qualification_option', 'MISSING')}'")
print(f"   utility_program value: {form_data.get('utility_program', 'MISSING')}")
print(f"   documentation value: {form_data.get('documentation', 'MISSING')}")

# Check if the form fields are being processed at all
if 'qualification_option' not in form_data:
    print("   ❌ qualification_option NOT found in form_data!")
if 'utility_program' not in form_data:
    print("   ❌ utility_program NOT found in form_data!")
if 'documentation' not in form_data:
    print("   ❌ documentation NOT found in form_data!")
'''
    
    print(debug_code2)
    print()
    
    print("🔍 Then run the app and have the user submit a form. Check the console output for:")
    print("   1. Whether qualification_option, utility_program, documentation are being received")
    print("   2. What values they contain")
    print("   3. Whether the qualification processing section is reached")
    print()
    
    print("🚨 POSSIBLE ISSUES TO CHECK:")
    print("   1. Frontend form HTML: Are the qualification checkboxes named correctly?")
    print("   2. Form submission: Is the form being submitted with the right field names?")
    print("   3. Flask form processing: Are the getlist() calls working for checkboxes?")
    print("   4. User behavior: Is the user actually selecting qualification options?")
    print()
    
    # Let's also check what the frontend form should look like
    print("📝 The frontend form should have HTML like this:")
    print()
    
    html_example = '''
<!-- Section 3: Qualification -->
<fieldset>
    <legend>Section 3: Income Qualification</legend>
    
    <div>
        <label>Qualification Option:</label>
        
        <input type="radio" name="qualification_option" value="option_a" id="option_a">
        <label for="option_a">Option A: Utility Programs</label>
        
        <div id="option_a_details" style="margin-left: 20px;">
            <input type="checkbox" name="utility_program" value="electric_discount" id="electric_discount">
            <label for="electric_discount">Electric Discount</label>
            
            <input type="checkbox" name="utility_program" value="low_income_discount" id="low_income_discount">
            <label for="low_income_discount">Low Income Program</label>
            
            <input type="checkbox" name="utility_program" value="bill_forgiveness" id="bill_forgiveness">
            <label for="bill_forgiveness">Bill Forgiveness Program</label>
        </div>
        
        <input type="radio" name="qualification_option" value="option_b" id="option_b">
        <label for="option_b">Option B: Documentation</label>
        
        <div id="option_b_details" style="margin-left: 20px;">
            <input type="checkbox" name="documentation" value="ebt_award" id="ebt_award">
            <label for="ebt_award">EBT (Food Stamps)</label>
        </div>
    </div>
</fieldset>
'''
    
    print(html_example)
    print()
    
    print("📋 NEXT STEPS:")
    print("   1. Add the debugging code to app.py")
    print("   2. Run the app and test a form submission")
    print("   3. Check the console output to see what's being received")
    print("   4. If qualification fields are missing, check the frontend HTML")
    print("   5. If qualification fields are there but empty, check user behavior")

if __name__ == "__main__":
    debug_user_form_data()