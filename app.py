from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import json
import base64
from io import BytesIO

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock data for development (matching your React wireframe data)
MOCK_DOCUMENTS = [
    {
        'id': '1',
        'name': 'Employment Contract',
        'status': 'Awaiting User 2',
        'lastUpdated': '2 hours ago',
        'created_at': datetime.now().isoformat(),
        'user1_data': {'name': 'John Doe', 'email': 'john@example.com'}
    },
    {
        'id': '2', 
        'name': 'Rental Agreement',
        'status': 'Signed & Sent',
        'lastUpdated': '1 day ago',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'user1_data': {'name': 'Alice Smith', 'email': 'alice@example.com'},
        'user2_data': {'name': 'Bob Johnson', 'email': 'bob@example.com'}
    },
    {
        'id': '3',
        'name': 'Insurance Form', 
        'status': 'Awaiting User 1',
        'lastUpdated': '3 days ago',
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'working_example',
        'name': 'Working Example with Field Values.pdf',
        'status': 'Signed & Sent',
        'lastUpdated': 'Just created',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'user1_data': {
            'name': 'John Test User',
            'email': 'john@test.com',
            'employee_id': 'TEST001',
            'department': 'Testing'
        },
        'user2_data': {
            'name': 'Jane Test Manager',
            'email': 'jane@test.com',
            'signature': 'Jane Test Manager',
            'date_signed': datetime.now().isoformat()
        },
        'pdf_fields': [
            {
                'id': 'working_field_1',
                'name': 'Employee Full Name',
                'type': 'text',
                'value': 'John Test User - Employee',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_2',
                'name': 'Employee Email Address',
                'type': 'email',
                'value': 'john.employee@company.com',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_3',
                'name': 'Employee Phone',
                'type': 'tel',
                'value': '+1-555-TEST-001',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_4',
                'name': 'Employee Department',
                'type': 'text',
                'value': 'Software Engineering',
                'assigned_to': 'user1',
                'source': 'working_example'
            },
            {
                'id': 'working_field_5',
                'name': 'Manager Name',
                'type': 'text',
                'value': 'Jane Test Manager - Supervisor',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_6',
                'name': 'Manager Signature',
                'type': 'signature',
                'value': 'Jane Test Manager Digital Signature',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_7',
                'name': 'Approval Notes',
                'type': 'textarea',
                'value': 'This employee has been approved for the position. All requirements have been met and background checks completed successfully.',
                'assigned_to': 'user2',
                'source': 'working_example'
            },
            {
                'id': 'working_field_8',
                'name': 'Start Date',
                'type': 'date',
                'value': '2024-02-01',
                'assigned_to': 'user1',
                'source': 'working_example'
            }
        ]
    }
]

def get_documents():
    """Get documents (mock data for now)"""
    return MOCK_DOCUMENTS

def get_document_by_id(document_id):
    """Get single document by ID"""
    return next((doc for doc in MOCK_DOCUMENTS if doc['id'] == document_id), None)

def extract_pdf_fields(pdf_path):
    """Enhanced PDF field extraction with comprehensive detection methods"""
    fields = []
    
    try:
        print(f"🔍 Analyzing PDF: {pdf_path}")
        
        # Check if file exists first
        if not os.path.exists(pdf_path):
            print(f"⚠️  PDF file not found: {pdf_path}")
            print("📝 Creating intelligent default fields...")
            # Skip to Method 4 (intelligent defaults)
            fields = []
        else:
            # Method 1: Extract actual PDF form fields using PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    return {"error": "PDF is encrypted and cannot be processed"}
                
                print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                
                # Check for AcroForm fields
                if '/AcroForm' in pdf_reader.trailer['/Root']:
                    acro_form = pdf_reader.trailer['/Root']['/AcroForm']
                    print("✅ Found AcroForm in PDF")
                    
                    if '/Fields' in acro_form:
                        form_fields = acro_form['/Fields']
                        print(f"📋 Found {len(form_fields)} form fields")
                        
                        for i, field in enumerate(form_fields):
                            field_obj = field.get_object()
                            field_name = field_obj.get('/T', f'acro_field_{i}')
                            field_type = field_obj.get('/FT', '/Tx')
                            field_value = field_obj.get('/V', '')
                            
                            # Store the original field name for exact matching
                            original_field_name = str(field_name) if field_name else f'acro_field_{i}'
                            
                            # Determine field type
                            if field_type == '/Tx':
                                field_input_type = 'text'
                            elif field_type == '/Btn':
                                field_input_type = 'checkbox'
                            elif field_type == '/Ch':
                                field_input_type = 'select'
                            else:
                                field_input_type = 'text'
                            
                            # Get field position
                            if '/Rect' in field_obj:
                                rect = field_obj['/Rect']
                                x, y, width, height = rect
                            else:
                                x, y, width, height = 100 + (i % 3) * 200, 700 - (i // 3) * 50, 180, 25
                            
                            # Determine likely user assignment based on field name
                            field_name_lower = original_field_name.lower()
                            if any(keyword in field_name_lower for keyword in ['signature', 'sign', 'approve', 'manager', 'supervisor', 'hr']):
                                assigned_to = 'user2'
                            else:
                                assigned_to = 'user1'
                            
                            fields.append({
                                'id': original_field_name,  # Use original field name as ID for exact matching
                                'name': original_field_name,  # Keep original name for display and matching
                                'type': field_input_type,
                                'value': str(field_value) if field_value else '',
                                'position': {'x': float(x), 'y': float(y), 'width': float(width), 'height': float(height)},
                                'assigned_to': assigned_to,
                                'page': 0,
                                'source': 'acroform',
                                'pdf_field_name': original_field_name  # Store for exact matching
                            })
                            
                else:
                    print("ℹ️  No AcroForm found in PDF")
        
        # Method 4: Create intelligent defaults if no fields found
        if not fields:
            print("📝 Creating intelligent default fields...")
            default_fields = [
                {'name': 'Full Name', 'type': 'text', 'assigned_to': 'user1'},
                {'name': 'Email Address', 'type': 'email', 'assigned_to': 'user1'},
                {'name': 'Phone Number', 'type': 'tel', 'assigned_to': 'user1'},
                {'name': 'Date', 'type': 'date', 'assigned_to': 'user1'},
                {'name': 'Address', 'type': 'text', 'assigned_to': 'user1'},
                {'name': 'Employee ID', 'type': 'text', 'assigned_to': 'user1'},
                {'name': 'Department', 'type': 'text', 'assigned_to': 'user1'},
                {'name': 'Position/Title', 'type': 'text', 'assigned_to': 'user1'},
                {'name': 'Manager Name', 'type': 'text', 'assigned_to': 'user2'},
                {'name': 'Manager Signature', 'type': 'signature', 'assigned_to': 'user2'},
                {'name': 'HR Approval', 'type': 'text', 'assigned_to': 'user2'},
                {'name': 'Approval Date', 'type': 'date', 'assigned_to': 'user2'},
                {'name': 'Additional Notes', 'type': 'textarea', 'assigned_to': 'user2'},
            ]
            
            for i, field_data in enumerate(default_fields):
                fields.append({
                    'id': f'default_{i}',
                    'name': field_data['name'],
                    'type': field_data['type'],
                    'value': '',
                    'position': {
                        'x': 100 + (i % 2) * 250,
                        'y': 700 - (i // 2) * 60,
                        'width': 200,
                        'height': 30 if field_data['type'] != 'textarea' else 60
                    },
                    'assigned_to': field_data['assigned_to'],
                    'page': 0,
                    'source': 'defaults'
                })
        
        print(f"✅ Total fields extracted: {len(fields)}")
        for field in fields:
            print(f"   - {field['name']} ({field['type']}) → {field['assigned_to']} [{field['source']}]")
            
    except Exception as e:
        print(f"❌ Error extracting PDF fields: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to process PDF: {str(e)}"}
    
    return {"fields": fields}

def convert_pdf_to_image(pdf_path, page_num=0):
    """Convert PDF page to image for display"""
    try:
        # This would require pdf2image in production
        # For now, return a placeholder
        return "/static/placeholder-pdf.png"
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        return "/static/placeholder-pdf.png"

def generate_completed_pdf(document):
    """Generate a completed PDF with all field values filled"""
    try:
        print(f"🎯 Generating completed PDF for document: {document['name']}")
        print(f"📊 Document has keys: {list(document.keys())}")
        
        # Debug: print document data
        if 'pdf_fields' in document:
            print(f"📋 PDF fields count: {len(document['pdf_fields'])}")
            for field in document['pdf_fields'][:3]:  # Show first 3 fields
                print(f"   - {field.get('name', 'unnamed')}: '{field.get('value', '')}' → {field.get('assigned_to', 'unassigned')}")
        
        if 'user1_data' in document:
            print(f"👤 User 1 data: {list(document['user1_data'].keys())}")
            
        if 'user2_data' in document:
            print(f"👥 User 2 data: {list(document['user2_data'].keys())}")
        
        # Check if we have the original PDF file
        if 'file_path' not in document or not os.path.exists(document['file_path']):
            print("❌ Original PDF file not found, generating summary PDF")
            return generate_summary_pdf(document)
        
        print(f"📄 Original PDF found: {document['file_path']}")
        
        # Create output path
        output_filename = f"completed_{document['id']}_{document['name']}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        print(f"📁 Output path: {output_path}")
        
        # Try to fill the original PDF first
        print("🔧 Attempting to fill original PDF...")
        if fill_pdf_fields_advanced(document['file_path'], document, output_path):
            print(f"✅ Successfully filled original PDF: {output_path}")
            return output_path
        else:
            print("⚠️  Could not fill original PDF, generating summary PDF instead")
            return generate_summary_pdf(document)
            
    except Exception as e:
        print(f"❌ Error generating completed PDF: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Falling back to summary PDF generation...")
        return generate_summary_pdf(document)

def fill_pdf_fields_advanced(pdf_path, document, output_path):
    """Advanced PDF field filling with better field matching"""
    try:
        with open(pdf_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            pdf_writer = PyPDF2.PdfWriter()
            
            print(f"📄 Processing PDF with {len(pdf_reader.pages)} pages")
            
            # Create a mapping of field names to values from our extracted fields
            field_mapping = {}
            
            # Map PDF field values using the original field names/IDs from extraction
            if 'pdf_fields' in document:
                for field in document['pdf_fields']:
                    if field.get('value'):
                        # Use the original field name from the PDF extraction
                        original_name = field['name']
                        field_id = field.get('id', '')
                        field_value = field['value']
                        pdf_field_name = field.get('pdf_field_name', original_name)
                        
                        # Map using exact field names first (highest priority)
                        field_mapping[pdf_field_name] = field_value
                        field_mapping[original_name] = field_value
                        field_mapping[field_id] = field_value
                        
                        # Also map lowercase versions for fallback
                        field_mapping[pdf_field_name.lower()] = field_value
                        field_mapping[original_name.lower()] = field_value
                        
                        print(f"📝 Mapping field: '{pdf_field_name}' = '{field_value}'")
            
            print(f"📋 Created {len(field_mapping)} field mappings")
            filled_count = 0
            
            # Method 1: Try to fill using AcroForm fields directly
            if '/AcroForm' in pdf_reader.trailer.get('/Root', {}):
                acro_form = pdf_reader.trailer['/Root']['/AcroForm']
                print("✅ Found AcroForm in PDF")
                
                if '/Fields' in acro_form:
                    form_fields = acro_form['/Fields']
                    print(f"📋 Found {len(form_fields)} form fields in AcroForm")
                    
                    for i, field_ref in enumerate(form_fields):
                        try:
                            field_obj = field_ref.get_object()
                            if '/T' in field_obj:
                                field_name = str(field_obj['/T'])
                                print(f"🔍 Processing form field: '{field_name}'")
                                
                                # Look for a matching value in our mapping
                                field_value = None
                                
                                # Try exact match first
                                if field_name in field_mapping:
                                    field_value = field_mapping[field_name]
                                # Try lowercase match
                                elif field_name.lower() in field_mapping:
                                    field_value = field_mapping[field_name.lower()]
                                # Try partial matches
                                else:
                                    for mapped_name, mapped_value in field_mapping.items():
                                        if (mapped_name.lower() in field_name.lower() or 
                                            field_name.lower() in mapped_name.lower()):
                                            field_value = mapped_value
                                            break
                                
                                if field_value:
                                    try:
                                        # Fill the field value
                                        field_obj.update({
                                            PyPDF2.generic.NameObject('/V'): 
                                            PyPDF2.generic.TextStringObject(str(field_value))
                                        })
                                        filled_count += 1
                                        print(f"✅ Filled field '{field_name}' with '{field_value}'")
                                    except Exception as e:
                                        print(f"⚠️  Could not fill field '{field_name}': {e}")
                                else:
                                    print(f"⭕ No value found for field '{field_name}'")
                        except Exception as e:
                            print(f"⚠️  Error processing field {i}: {e}")
            
            # Method 2: Also try annotation-based approach for additional coverage
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        try:
                            annotation_obj = annotation.get_object()
                            if '/T' in annotation_obj and '/Subtype' in annotation_obj:
                                subtype = annotation_obj['/Subtype']
                                if subtype == '/Widget':  # Form field widget
                                    field_name = str(annotation_obj['/T'])
                                    
                                    # Skip if we already filled this field
                                    if any(field_name in str(filled) for filled in range(filled_count)):
                                        continue
                                    
                                    # Look for value
                                    field_value = None
                                    if field_name in field_mapping:
                                        field_value = field_mapping[field_name]
                                    elif field_name.lower() in field_mapping:
                                        field_value = field_mapping[field_name.lower()]
                                    
                                    if field_value:
                                        try:
                                            annotation_obj.update({
                                                PyPDF2.generic.NameObject('/V'): 
                                                PyPDF2.generic.TextStringObject(str(field_value))
                                            })
                                            filled_count += 1
                                            print(f"✅ Filled annotation field '{field_name}' with '{field_value}'")
                                        except Exception as e:
                                            print(f"⚠️  Could not fill annotation field '{field_name}': {e}")
                        except Exception as e:
                            continue
                
                pdf_writer.add_page(page)
            
            # Write the filled PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            print(f"✅ Successfully filled {filled_count} fields in original PDF")
            
            # Only consider it successful if we actually filled some fields
            if filled_count > 0:
                return True
            else:
                print("⚠️  No fields were actually filled in original PDF")
                return False
                
    except Exception as e:
        print(f"❌ Error in fill_pdf_fields_advanced: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_summary_pdf(document):
    """Generate a summary PDF when original PDF filling fails"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        output_filename = f"summary_{document['id']}_{document['name']}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=20
        )
        story.append(Paragraph(f"Completed Document: {document['name']}", title_style))
        story.append(Spacer(1, 20))
        
        # Document info
        info_data = [
            ['Document ID:', document['id']],
            ['Status:', document.get('status', 'Completed')],
            ['Completed:', document.get('completed_at', 'Recently')[:10] if document.get('completed_at') else 'Recently']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # User 1 Information
        if document.get('user1_data'):
            story.append(Paragraph("User 1 Information", styles['Heading2']))
            user1_data = []
            for key, value in document['user1_data'].items():
                if value:
                    user1_data.append([key.replace('_', ' ').title(), str(value)])
            
            if user1_data:
                user1_table = Table(user1_data, colWidths=[2*inch, 4*inch])
                user1_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(user1_table)
                story.append(Spacer(1, 20))
        
        # PDF Fields
        if document.get('pdf_fields'):
            story.append(Paragraph("Completed Form Fields", styles['Heading2']))
            
            # Add header row
            field_data = [['Field Name', 'Value', 'Completed By']]
            
            for field in document['pdf_fields']:
                if field.get('value'):
                    user_label = "User 1" if field['assigned_to'] == 'user1' else "User 2"
                    field_data.append([
                        field['name'],
                        field['value'],
                        user_label
                    ])
            
            if len(field_data) > 1:  # More than just header
                field_table = Table(field_data, colWidths=[2.5*inch, 3*inch, 1*inch])
                field_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(field_table)
                story.append(Spacer(1, 20))
            else:
                story.append(Paragraph("No field values were provided.", styles['Normal']))
                story.append(Spacer(1, 20))
        
        # User 2 Information
        if document.get('user2_data'):
            story.append(Paragraph("User 2 Information", styles['Heading2']))
            user2_data = []
            for key, value in document['user2_data'].items():
                if value and key != 'signature':
                    user2_data.append([key.replace('_', ' ').title(), str(value)])
            
            if user2_data:
                user2_table = Table(user2_data, colWidths=[2*inch, 4*inch])
                user2_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(user2_table)
        
        # Build PDF
        doc.build(story)
        print(f"✅ Generated summary PDF: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating summary PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def fill_pdf_fields(pdf_path, field_data, output_path):
    """Legacy PDF field filling function"""
    return fill_pdf_fields_advanced(pdf_path, {'pdf_fields': [], 'user1_data': field_data, 'user2_data': {}}, output_path)

@app.route('/')
def dashboard():
    """Home/Dashboard page - matches your React Dashboard component"""
    documents = get_documents()
    return render_template('dashboard.html', documents=documents)

@app.route('/start-workflow')
def start_workflow():
    """Start new PDF workflow"""
    return redirect(url_for('user1_interface'))

@app.route('/user1', methods=['GET', 'POST'])
def user1_interface():
    """User 1 interface - matches your React UserOneInterface component"""
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            document_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_{filename}")
            file.save(file_path)
            
            # Get form data from User 1
            user1_data = {
                'name': request.form.get('user1_name', ''),
                'email': request.form.get('user1_email', ''),
                'employee_id': request.form.get('employee_id', ''),
                'department': request.form.get('department', ''),
                'position': request.form.get('position', ''),
                'start_date': request.form.get('start_date', ''),
                'salary': request.form.get('salary', ''),
                'employment_type': request.form.get('employment_type', ''),
                'address': request.form.get('address', '')
            }
            
            # Extract PDF fields
            pdf_analysis = extract_pdf_fields(file_path)
            if "error" in pdf_analysis:
                flash(f'Error processing PDF: {pdf_analysis["error"]}', 'error')
                return redirect(request.url)
            
            # Process PDF fields data from User 1
            pdf_fields_data = request.form.get('pdf_fields')
            print(f"📋 PDF fields data received: {pdf_fields_data is not None}")
            
            if pdf_fields_data:
                try:
                    # Parse the PDF fields JSON data from frontend
                    frontend_fields = json.loads(pdf_fields_data)
                    print(f"📊 Parsed {len(frontend_fields)} fields from frontend")
                    
                    # Debug: Show what we received
                    for i, field in enumerate(frontend_fields[:3]):  # Show first 3
                        print(f"   Frontend field {i+1}: {field.get('name', 'unnamed')} = '{field.get('value', '')}' → {field.get('assigned_to', 'unassigned')}")
                    
                    # Update the extracted fields with User 1's assignments and values
                    for frontend_field in frontend_fields:
                        # Find corresponding field in extracted fields
                        for extracted_field in pdf_analysis['fields']:
                            if extracted_field['id'] == frontend_field['id']:
                                # Update assignment and value
                                extracted_field['assigned_to'] = frontend_field.get('assigned_to', extracted_field['assigned_to'])
                                extracted_field['value'] = frontend_field.get('value', '')
                                if frontend_field.get('value'):
                                    print(f"✅ User 1 filled '{extracted_field['name']}': '{frontend_field['value']}'")
                                break
                        else:
                            # This is a custom field added by User 1
                            pdf_analysis['fields'].append(frontend_field)
                            if frontend_field.get('value'):
                                print(f"✅ User 1 added custom field '{frontend_field['name']}': '{frontend_field['value']}'")
                    
                    print(f"📊 Final field summary:")
                    for field in pdf_analysis['fields']:
                        if field.get('value'):
                            print(f"   ✅ {field['name']}: '{field['value']}' → {field['assigned_to']}")
                        else:
                            print(f"   ⭕ {field['name']}: (empty) → {field['assigned_to']}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing PDF fields JSON: {e}")
            else:
                print("⚠️  No PDF fields data received from User 1")
            
            # Add to mock data
            new_document = {
                'id': document_id,
                'name': filename,
                'status': 'Awaiting User 2',
                'lastUpdated': 'Just now',
                'created_at': datetime.now().isoformat(),
                'user1_data': user1_data,
                'file_path': file_path,
                'pdf_fields': pdf_analysis['fields'],
                'field_assignments': {field['id']: field['assigned_to'] for field in pdf_analysis['fields']}
            }
            
            print(f"📄 Adding new document to MOCK_DOCUMENTS:")
            print(f"   📋 Document ID: {document_id}")
            print(f"   📋 Document name: {filename}")
            print(f"   📋 PDF fields count: {len(pdf_analysis['fields'])}")
            
            # Show field values being saved
            fields_with_values = [f for f in pdf_analysis['fields'] if f.get('value')]
            fields_without_values = [f for f in pdf_analysis['fields'] if not f.get('value')]
            
            print(f"   ✅ Fields with values: {len(fields_with_values)}")
            for field in fields_with_values:
                print(f"      - {field['name']}: '{field['value']}' → {field['assigned_to']}")
            
            print(f"   ⭕ Fields without values: {len(fields_without_values)}")
            for field in fields_without_values:
                print(f"      - {field['name']}: (empty) → {field['assigned_to']}")
            
            MOCK_DOCUMENTS.append(new_document)
            
            flash('Document uploaded and sent to User 2!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type. Please upload a PDF file.', 'error')
    
    return render_template('user1_enhanced.html')

@app.route('/user2/<document_id>', methods=['GET', 'POST'])
def user2_interface(document_id):
    """User 2 interface - matches your React UserTwoInterface component"""
    document = get_document_by_id(document_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get User 2's contact information
        user2_data = {
            'name': request.form.get('user2_name', ''),
            'email': request.form.get('user2_email', ''),
            'signature': request.form.get('signature', ''),
            'date_signed': datetime.now().isoformat()
        }
        
        # Process User 2's PDF field values
        print(f"👥 Processing User 2 form for document: {document_id}")
        print(f"📊 Document has pdf_fields: {'pdf_fields' in document}")
        
        if 'pdf_fields' in document:
            print(f"📋 Found {len(document['pdf_fields'])} PDF fields in document")
            user2_fields = [f for f in document['pdf_fields'] if f['assigned_to'] == 'user2']
            print(f"📝 User 2 is assigned {len(user2_fields)} fields:")
            
            for field in user2_fields:
                print(f"   - {field['name']} ({field['id']}) → looking for form field 'field_{field['id']}'")
            
            for field in document['pdf_fields']:
                if field['assigned_to'] == 'user2':
                    # Get the field value from the form
                    field_value = request.form.get(f"field_{field['id']}", '')
                    print(f"🔍 Field '{field['name']}' ({field['id']}): form value = '{field_value}'")
                    
                    if field_value:
                        field['value'] = field_value
                        print(f"✅ User 2 filled field '{field['name']}': '{field_value}'")
                    else:
                        print(f"⭕ User 2 left field '{field['name']}' empty")
        else:
            print("❌ No pdf_fields found in document")
        
        # Also capture any legacy field names for backwards compatibility
        legacy_fields = {
            'manager': request.form.get('manager', ''),
            'hr_rep': request.form.get('hr_rep', ''),
            'benefits': request.form.get('benefits', ''),
            'notes': request.form.get('notes', ''),
            'manager_name': request.form.get('manager_name', ''),
            'hr_approval': request.form.get('hr_approval', ''),
            'approval_date': request.form.get('approval_date', ''),
            'hr_notes': request.form.get('hr_notes', '')
        }
        
        # Add non-empty legacy fields to user2_data
        for key, value in legacy_fields.items():
            if value:
                user2_data[key] = value
        
        # Handle supporting documents
        supporting_docs = []
        if 'supporting_docs' in request.files:
            for file in request.files.getlist('supporting_docs'):
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    support_path = os.path.join(app.config['UPLOAD_FOLDER'], f"support_{document_id}_{filename}")
                    file.save(support_path)
                    supporting_docs.append({'filename': filename, 'path': support_path})
        
        # Update document
        for doc in MOCK_DOCUMENTS:
            if doc['id'] == document_id:
                doc.update({
                    'status': 'Signed & Sent',
                    'user2_data': user2_data,
                    'supporting_docs': supporting_docs,
                    'completed_at': datetime.now().isoformat(),
                    'lastUpdated': 'Just now'
                })
                break
        
        return redirect(url_for('completion_page', document_id=document_id))
    
    return render_template('user2_enhanced.html', document=document)

@app.route('/complete/<document_id>')
def completion_page(document_id):
    """Completion page - matches your React CompletionPage component"""
    document = get_document_by_id(document_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('completion.html', document=document)

@app.route('/download/<document_id>')
def download_document(document_id):
    """Download completed PDF document"""
    print(f"🔽 Download request for document: {document_id}")
    
    document = get_document_by_id(document_id)
    if not document:
        print(f"❌ Document not found: {document_id}")
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"📋 Document found: {document.get('name', 'unknown')}")
    print(f"📊 Document data keys: {list(document.keys())}")
    
    # Debug: Show field values at download time
    if 'pdf_fields' in document:
        fields_with_values = [f for f in document['pdf_fields'] if f.get('value')]
        fields_without_values = [f for f in document['pdf_fields'] if not f.get('value')]
        
        print(f"📋 At download time - Fields with values: {len(fields_with_values)}")
        for field in fields_with_values:
            print(f"   ✅ {field['name']}: '{field['value']}' → {field['assigned_to']}")
        
        print(f"📋 At download time - Fields without values: {len(fields_without_values)}")
        for field in fields_without_values:
            print(f"   ⭕ {field['name']}: (empty) → {field['assigned_to']}")
    else:
        print("❌ No pdf_fields in document at download time")
    
    try:
        # Generate the completed PDF
        print("🎯 Starting PDF generation...")
        output_path = generate_completed_pdf(document)
        
        if output_path and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PDF generated successfully: {output_path} ({file_size} bytes)")
            
            # Validate PDF before sending
            with open(output_path, 'rb') as f:
                header = f.read(10)
                if not header.startswith(b'%PDF'):
                    print(f"❌ Invalid PDF header: {header}")
                    flash('Generated PDF appears to be corrupted. Please try again.', 'error')
                    return redirect(url_for('completion_page', document_id=document_id))
            
            print("📤 Sending PDF file for download...")
            
            # Return the file for download with improved headers
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"completed_{document['name']}",
                mimetype='application/pdf'
            )
        else:
            print("❌ PDF generation failed - no output file")
            flash('Error generating PDF. Please try again.', 'error')
            return redirect(url_for('completion_page', document_id=document_id))
            
    except Exception as e:
        print(f"❌ Error in download_document: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error generating PDF download: {str(e)}', 'error')
        return redirect(url_for('completion_page', document_id=document_id))

@app.route('/api/pdf-fields/<document_id>')
def get_pdf_fields(document_id):
    """API endpoint to get PDF fields for a document"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    if 'pdf_fields' in document:
        return jsonify({
            'fields': document['pdf_fields'],
            'assignments': document.get('field_assignments', {})
        })
    
    # If no fields extracted yet, try to extract them
    if 'file_path' in document:
        pdf_analysis = extract_pdf_fields(document['file_path'])
        if 'error' in pdf_analysis:
            return jsonify({'error': pdf_analysis['error']}), 500
        
        # Update document with fields
        document['pdf_fields'] = pdf_analysis['fields']
        document['field_assignments'] = {field['id']: field['assigned_to'] for field in pdf_analysis['fields']}
        
        return jsonify({
            'fields': document['pdf_fields'],
            'assignments': document['field_assignments']
        })
    
    return jsonify({'error': 'No PDF file found'}), 404

@app.route('/api/assign-field/<document_id>', methods=['POST'])
def assign_field(document_id):
    """API endpoint to assign a field to a user"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    field_id = data.get('field_id')
    assigned_to = data.get('assigned_to')
    
    if not field_id or not assigned_to:
        return jsonify({'error': 'Missing field_id or assigned_to'}), 400
    
    if assigned_to not in ['user1', 'user2']:
        return jsonify({'error': 'Invalid assigned_to value'}), 400
    
    # Update field assignment
    if 'field_assignments' not in document:
        document['field_assignments'] = {}
    
    document['field_assignments'][field_id] = assigned_to
    
    # Also update the field in pdf_fields if it exists
    if 'pdf_fields' in document:
        for field in document['pdf_fields']:
            if field['id'] == field_id:
                field['assigned_to'] = assigned_to
                break
    
    return jsonify({'success': True, 'field_id': field_id, 'assigned_to': assigned_to})

@app.route('/api/update-field/<document_id>', methods=['POST'])
def update_field_value(document_id):
    """API endpoint to update a field value"""
    document = get_document_by_id(document_id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    field_id = data.get('field_id')
    value = data.get('value')
    
    if not field_id:
        return jsonify({'error': 'Missing field_id'}), 400
    
    # Update field value
    if 'pdf_fields' in document:
        for field in document['pdf_fields']:
            if field['id'] == field_id:
                field['value'] = value
                break
    
    return jsonify({'success': True, 'field_id': field_id, 'value': value})

@app.route('/api/extract-fields', methods=['POST'])
def extract_fields_api():
    """API endpoint to extract fields from uploaded PDF"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        # Extract PDF fields
        pdf_analysis = extract_pdf_fields(temp_path)
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        if "error" in pdf_analysis:
            return jsonify({'error': pdf_analysis['error']}), 500
        
        return jsonify({
            'fields': pdf_analysis['fields'],
            'message': f'Successfully extracted {len(pdf_analysis["fields"])} fields from PDF'
        })
        
    except Exception as e:
        # Clean up temporary file on error
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        
        print(f"Error in extract_fields_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500

@app.route('/api/pdf-preview/<document_id>')
def get_pdf_preview(document_id):
    """API endpoint to get PDF preview image"""
    document = get_document_by_id(document_id)
    if not document or 'file_path' not in document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Convert PDF to image (placeholder for now)
    image_url = convert_pdf_to_image(document['file_path'])
    
    return jsonify({
        'preview_url': image_url,
        'page_count': 1  # Placeholder
    })

if __name__ == '__main__':
    print("🚀 PDF Collaborator Flask App Starting...")
    print("📊 Using mock data for development")
    print("🌐 Access at: http://localhost:5006")
    app.run(debug=True, port=5006)