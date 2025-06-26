#!/usr/bin/env python3
"""
Test script to verify email functionality with Brevo
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.getcwd())

from email_utils import EmailService, is_email_configured

def test_email_configuration():
    """Test email configuration and send a test email"""
    print("🧪 Testing Email Configuration...")
    print("=" * 50)
    
    # Check if email is configured
    if not is_email_configured():
        print("❌ Email is not properly configured!")
        print("\nRequired environment variables:")
        print("- SMTP_SERVER")
        print("- SMTP_PORT") 
        print("- SMTP_USERNAME")
        print("- SMTP_PASSWORD")
        print("- FROM_EMAIL")
        return False
    
    print("✅ Email configuration found!")
    
    # Display configuration (without sensitive data)
    print(f"\n📧 Email Configuration:")
    print(f"SMTP Server: {os.getenv('SMTP_SERVER')}")
    print(f"SMTP Port: {os.getenv('SMTP_PORT')}")
    print(f"Username: {os.getenv('SMTP_USERNAME')}")
    print(f"From Email: {os.getenv('FROM_EMAIL')}")
    
    # Create email service instance
    email_service = EmailService()
    
    # Test email recipient (use the same email as sender for testing)
    test_recipient = os.getenv('SMTP_USERNAME')  # Use sender email for testing
    
    print(f"\n📤 Sending test email to: {test_recipient}")
    
    # Send test email
    subject = "🧪 PDFCollab Email Test"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Email Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #28a745; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Email Test Successful!</h1>
            </div>
            <div class="content">
                <h3>Congratulations!</h3>
                <p>Your PDFCollab email configuration is working correctly.</p>
                <p><strong>Test sent on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><strong>SMTP Server:</strong> {os.getenv('SMTP_SERVER')}</p>
                <p>You can now receive email notifications for:</p>
                <ul>
                    <li>Document completions</li>
                    <li>Welcome messages</li>
                    <li>Other notifications</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    PDFCollab Email Test

    Congratulations! Your email configuration is working correctly.

    Test sent on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    SMTP Server: {os.getenv('SMTP_SERVER')}

    You can now receive email notifications for:
    - Document completions
    - Welcome messages  
    - Other notifications

    --
    PDFCollab Email System
    """
    
    success = email_service.send_email(test_recipient, subject, html_content, text_content)
    
    if success:
        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox at: {test_recipient}")
        print("\n🎯 Email notifications are now working in your PDFCollab application!")
    else:
        print("❌ Failed to send test email!")
        print("Please check your email configuration and try again.")
    
    return success

def test_document_notification():
    """Test document completion notification"""
    print("\n🧪 Testing Document Completion Notification...")
    print("=" * 50)
    
    email_service = EmailService()
    test_recipient = os.getenv('SMTP_USERNAME')
    
    # Mock document data
    document_data = {
        'id': 'test_doc_123',
        'name': 'Test Contract.pdf',
        'status': 'Signed & Sent',
        'user1_email': test_recipient,
    }
    
    success = email_service.send_document_completion_notification(document_data, test_recipient)
    
    if success:
        print("✅ Document completion notification sent successfully!")
    else:
        print("❌ Failed to send document completion notification!")
    
    return success

if __name__ == "__main__":
    print("🚀 PDFCollab Email Testing Suite")
    print("=" * 50)
    
    # Test basic email configuration
    config_test = test_email_configuration()
    
    if config_test:
        # Test document notification
        doc_test = test_document_notification()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"✅ Email Configuration: {'PASSED' if config_test else 'FAILED'}")
        print(f"✅ Document Notification: {'PASSED' if doc_test else 'FAILED'}")
        
        if config_test and doc_test:
            print("\n🎉 All email tests passed! Your Brevo integration is working perfectly.")
        else:
            print("\n⚠️  Some tests failed. Please check the configuration and try again.")
    else:
        print("\n❌ Email configuration test failed. Please fix the configuration first.")