#!/usr/bin/env python3
"""
Test script for invitation email functionality
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.getcwd())

from email_utils import send_document_invitation_email, is_email_configured

def test_invitation_email():
    """Test the document invitation email functionality"""
    print("🧪 Testing Document Invitation Email...")
    print("=" * 50)
    
    # Check if email is configured
    if not is_email_configured():
        print("❌ Email is not properly configured!")
        return False
    
    print("✅ Email configuration found!")
    
    # Test recipient email
    test_recipient = "se7nz7@gmail.com"  # User 2 email from your test
    sender_name = "John Doe"  # User 1 name
    
    # Mock document data (similar to your actual document structure)
    document_data = {
        'id': 'test_invitation_123',
        'name': 'Employment Contract.pdf',
        'status': 'Pending User 2',
        'user1_data': {
            'name': sender_name,
            'email': 'cvsper813@gmail.com',
            'user2_email': test_recipient
        }
    }
    
    # Generate invitation URL (simulated)
    invitation_url = f"http://localhost:5006/user2/{document_data['id']}"
    
    print(f"📧 Sending invitation email to: {test_recipient}")
    print(f"📤 From: {sender_name}")
    print(f"📄 Document: {document_data['name']}")
    print(f"🔗 Invitation URL: {invitation_url}")
    
    # Send invitation email
    success = send_document_invitation_email(
        document_data=document_data,
        recipient_email=test_recipient,
        sender_name=sender_name,
        invitation_url=invitation_url
    )
    
    if success:
        print("✅ Invitation email sent successfully!")
        print(f"📬 Check the inbox at: {test_recipient}")
        print("\n📋 The invitation email includes:")
        print("  • Document details and sender information")
        print("  • Clear call-to-action button")
        print("  • Step-by-step instructions")
        print("  • Direct link to complete the document")
        print("  • Professional formatting")
    else:
        print("❌ Failed to send invitation email!")
        print("Please check your email configuration and try again.")
    
    return success

def test_multiple_invitations():
    """Test sending invitations to multiple recipients"""
    print("\n🧪 Testing Multiple Invitation Scenarios...")
    print("=" * 50)
    
    test_cases = [
        {
            'recipient': 'cvsper813@gmail.com',
            'sender': 'Sarah Smith',
            'document': 'NDA Agreement.pdf'
        },
        {
            'recipient': 'se7nz7@gmail.com', 
            'sender': 'Mike Johnson',
            'document': 'Service Contract.pdf'
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {case['document']}")
        
        document_data = {
            'id': f'test_multi_{i}',
            'name': case['document'],
            'status': 'Pending User 2',
            'user1_data': {
                'name': case['sender'],
                'user2_email': case['recipient']
            }
        }
        
        invitation_url = f"http://localhost:5006/user2/test_multi_{i}"
        
        success = send_document_invitation_email(
            document_data=document_data,
            recipient_email=case['recipient'],
            sender_name=case['sender'],
            invitation_url=invitation_url
        )
        
        if success:
            print(f"✅ Sent to {case['recipient']} from {case['sender']}")
            success_count += 1
        else:
            print(f"❌ Failed to send to {case['recipient']}")
    
    print(f"\n📊 Results: {success_count}/{len(test_cases)} invitations sent successfully")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("🚀 PDFCollab Invitation Email Testing Suite")
    print("=" * 50)
    
    # Test basic invitation functionality
    basic_test = test_invitation_email()
    
    if basic_test:
        # Test multiple scenarios
        multi_test = test_multiple_invitations()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"✅ Basic Invitation: {'PASSED' if basic_test else 'FAILED'}")
        print(f"✅ Multiple Invitations: {'PASSED' if multi_test else 'FAILED'}")
        
        if basic_test and multi_test:
            print("\n🎉 All invitation tests passed!")
            print("\n💡 How to use in your application:")
            print("1. Navigate to your dashboard at http://localhost:5006/dashboard")
            print("2. Find a document with 'Pending User 2' status")
            print("3. Click the 'Send Invite' button")
            print("4. User 2 will receive a professional email with:")
            print("   • Document details and sender info")
            print("   • Direct link to complete the document")
            print("   • Clear instructions on what to do")
            print("   • Professional branding")
        else:
            print("\n⚠️  Some tests failed. Please check the configuration and try again.")
    else:
        print("\n❌ Basic invitation test failed. Please fix the configuration first.")