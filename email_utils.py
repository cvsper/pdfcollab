#!/usr/bin/env python3
"""
Email utilities for sending notifications via Brevo SMTP
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from datetime import datetime
import traceback


class EmailService:
    """Email service using Brevo SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp-relay.brevo.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
    
    def is_configured(self):
        """Check if email is properly configured"""
        return all([
            self.smtp_server,
            self.smtp_port,
            self.smtp_username,
            self.smtp_password,
            self.from_email
        ])
    
    def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
        """
        Send an email using Brevo SMTP
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): HTML email content
            text_content (str, optional): Plain text content (fallback)
            attachments (list, optional): List of file paths to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            current_app.logger.error("Email not configured properly")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part (fallback)
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            # Log success (use print if no Flask context)
            try:
                current_app.logger.info(f"Email sent successfully to {to_email}")
            except RuntimeError:
                print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            # Log error (use print if no Flask context)
            try:
                current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
                current_app.logger.error(traceback.format_exc())
            except RuntimeError:
                print(f"❌ Failed to send email to {to_email}: {str(e)}")
                print(traceback.format_exc())
            return False
    
    def send_document_completion_notification(self, document_data, recipient_email):
        """Send notification when a document is completed"""
        subject = f"Document Completed: {document_data.get('name', 'PDF Document')}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Document Completed</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 10px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 PDFCollab</h1>
                    <h2>Document Completed Successfully</h2>
                </div>
                <div class="content">
                    <h3>Great news! Your document has been completed.</h3>
                    
                    <p><strong>Document:</strong> {document_data.get('name', 'PDF Document')}</p>
                    <p><strong>Status:</strong> {document_data.get('status', 'Completed')}</p>
                    <p><strong>Completed on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    
                    <p>The document has been signed and is ready for download.</p>
                    
                    <p style="text-align: center;">
                        <a href="https://pdfcollab.onrender.com/dashboard" class="button">
                            View in Dashboard
                        </a>
                    </p>
                    
                    <p>Thank you for using PDFCollab!</p>
                </div>
                <div class="footer">
                    <p>This email was sent from PDFCollab. If you have any questions, please contact support.</p>
                    <p>&copy; {datetime.now().year} PDFCollab. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        PDFCollab - Document Completed

        Great news! Your document has been completed.

        Document: {document_data.get('name', 'PDF Document')}
        Status: {document_data.get('status', 'Completed')}
        Completed on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

        The document has been signed and is ready for download.

        View in Dashboard: https://pdfcollab.onrender.com/dashboard

        Thank you for using PDFCollab!

        --
        This email was sent from PDFCollab.
        © {datetime.now().year} PDFCollab. All rights reserved.
        """
        
        return self.send_email(recipient_email, subject, html_content, text_content)
    
    def send_welcome_email(self, user_email, username):
        """Send welcome email for new user registration"""
        subject = "Welcome to PDFCollab!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to PDFCollab</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 10px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to PDFCollab!</h1>
                </div>
                <div class="content">
                    <h3>Hi {username},</h3>
                    
                    <p>Welcome to PDFCollab! We're excited to have you on board.</p>
                    
                    <p>With PDFCollab, you can:</p>
                    <ul>
                        <li>📝 Edit PDF documents online</li>
                        <li>👥 Collaborate with your team in real-time</li>
                        <li>✍️ Add digital signatures</li>
                        <li>💬 Add comments and annotations</li>
                        <li>🔒 Securely share documents</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="https://pdfcollab.onrender.com/dashboard" class="button">
                            Get Started Now
                        </a>
                    </p>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Happy collaborating!</p>
                </div>
                <div class="footer">
                    <p>This email was sent from PDFCollab.</p>
                    <p>&copy; {datetime.now().year} PDFCollab. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to PDFCollab!

        Hi {username},

        Welcome to PDFCollab! We're excited to have you on board.

        With PDFCollab, you can:
        - Edit PDF documents online
        - Collaborate with your team in real-time  
        - Add digital signatures
        - Add comments and annotations
        - Securely share documents

        Get Started: https://pdfcollab.onrender.com/dashboard

        If you have any questions, feel free to reach out to our support team.

        Happy collaborating!

        --
        This email was sent from PDFCollab.
        © {datetime.now().year} PDFCollab. All rights reserved.
        """
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_document_invitation(self, document_data, recipient_email, sender_name, invitation_url):
        """Send invitation email to User 2 to complete document"""
        subject = f"Document Signature Request: {document_data.get('name', 'PDF Document')}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Document Signature Request</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background: #28a745; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 15px 0; 
                    font-weight: bold;
                    font-size: 16px;
                }}
                .urgent {{ 
                    background: #ffc107; 
                    color: #000; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 10px 0; 
                    text-align: center; 
                }}
                .document-info {{
                    background: white;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Document Signature Required</h1>
                    <h2>PDFCollab</h2>
                </div>
                <div class="content">
                    <h3>Hi there,</h3>
                    
                    <p>{sender_name} has shared a document with you that requires your signature and completion.</p>
                    
                    <div class="document-info">
                        <h4>📋 Document Details:</h4>
                        <p><strong>Document:</strong> {document_data.get('name', 'PDF Document')}</p>
                        <p><strong>From:</strong> {sender_name}</p>
                        <p><strong>Status:</strong> Awaiting your signature</p>
                        <p><strong>Sent on:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div class="urgent">
                        ⏰ <strong>Action Required:</strong> Please review and sign this document
                    </div>
                    
                    <p>To complete your portion of the document:</p>
                    <ol>
                        <li>Click the "Complete Document" button below</li>
                        <li>Review the document content</li>
                        <li>Fill in any required fields</li>
                        <li>Add your digital signature</li>
                        <li>Submit the completed form</li>
                    </ol>
                    
                    <p style="text-align: center;">
                        <a href="{invitation_url}" class="button">
                            ✍️ Complete Document Now
                        </a>
                    </p>
                    
                    <p><small>This link is secure and will take you directly to the document completion page. No registration required.</small></p>
                    
                    <p>If you have any questions about this document, please contact {sender_name} directly.</p>
                    
                    <p>Thank you for using PDFCollab!</p>
                </div>
                <div class="footer">
                    <p>This email was sent from PDFCollab on behalf of {sender_name}.</p>
                    <p>If you believe you received this email in error, please ignore it.</p>
                    <p>&copy; {datetime.now().year} PDFCollab. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Document Signature Required - PDFCollab

        Hi there,

        {sender_name} has shared a document with you that requires your signature and completion.

        Document Details:
        - Document: {document_data.get('name', 'PDF Document')}
        - From: {sender_name}
        - Status: Awaiting your signature
        - Sent on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

        ACTION REQUIRED: Please review and sign this document

        To complete your portion of the document:
        1. Open this link: {invitation_url}
        2. Review the document content
        3. Fill in any required fields
        4. Add your digital signature
        5. Submit the completed form

        This link is secure and will take you directly to the document completion page. No registration required.

        If you have any questions about this document, please contact {sender_name} directly.

        Thank you for using PDFCollab!

        --
        This email was sent from PDFCollab on behalf of {sender_name}.
        If you believe you received this email in error, please ignore it.
        © {datetime.now().year} PDFCollab. All rights reserved.
        """
        
        return self.send_email(recipient_email, subject, html_content, text_content)


# Global email service instance
email_service = EmailService()


def send_document_completion_email(document_data, recipient_email):
    """Convenience function to send document completion notification"""
    return email_service.send_document_completion_notification(document_data, recipient_email)


def send_welcome_email(user_email, username):
    """Convenience function to send welcome email"""
    return email_service.send_welcome_email(user_email, username)


def send_document_invitation_email(document_data, recipient_email, sender_name, invitation_url):
    """Convenience function to send document invitation"""
    return email_service.send_document_invitation(document_data, recipient_email, sender_name, invitation_url)


def is_email_configured():
    """Check if email service is properly configured"""
    return email_service.is_configured()