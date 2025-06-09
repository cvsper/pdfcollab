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
                            field_name_lower = str(field_name).lower() if field_name else ''
                            if any(keyword in field_name_lower for keyword in ['signature', 'sign', 'approve', 'manager', 'supervisor', 'hr']):
                                assigned_to = 'user2'
                            else:
                                assigned_to = 'user1'
                            
                            fields.append({
                                'id': f'acro_{i}',
                                'name': str(field_name) if field_name else f'Form Field {i+1}',
                                'type': field_input_type,
                                'value': str(field_value) if field_value else '',
                                'position': {'x': float(x), 'y': float(y), 'width': float(width), 'height': float(height)},
                                'assigned_to': assigned_to,
                                'page': 0,
                                'source': 'acroform'
                            })
                        
                else:
                    print("ℹ️  No AcroForm found in PDF")
                
                # Method 2: Check for annotations on each page
                annotation_fields = []
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        annotations = page['/Annots']
                        print(f"📝 Found {len(annotations)} annotations on page {page_num + 1}")
                        
                        for j, annot in enumerate(annotations):
                            annot_obj = annot.get_object()
                            if '/Subtype' in annot_obj:
                                subtype = annot_obj['/Subtype']
                                
                                # Check for form field annotations
                                if subtype in ['/Widget', '/FreeText', '/Text']:
                                field_name = annot_obj.get('/T', f'annot_p{page_num}_{j}')
                                
                                # Get position
                                if '/Rect' in annot_obj:
                                    rect = annot_obj['/Rect']
                                    x, y, width, height = rect
                                else:
                                    x, y, width, height = 100 + (j % 3) * 200, 600 - (j // 3) * 50, 180, 25
                                
                                # Smart assignment based on field name
                                field_name_lower = str(field_name).lower() if field_name else ''
                                if any(keyword in field_name_lower for keyword in ['signature', 'sign', 'approve', 'manager', 'supervisor', 'hr']):
                                    assigned_to = 'user2'
                                else:
                                    assigned_to = 'user1'
                                
                                annotation_fields.append({
                                    'id': f'annot_p{page_num}_{j}',
                                    'name': str(field_name) if field_name else f'Field (Page {page_num + 1})',
                                    'type': 'text',
                                    'value': '',
                                    'position': {'x': float(x), 'y': float(y), 'width': float(width), 'height': float(height)},
                                    'assigned_to': assigned_to,
                                    'page': page_num,
                                    'source': 'annotation'
                                })
            
            # Add annotation fields if no AcroForm fields found
            if not fields and annotation_fields:
                fields.extend(annotation_fields)
                print(f"📝 Added {len(annotation_fields)} annotation fields")
        
        # Method 3: Advanced text analysis with pdfplumber
        if not fields:
            print("🔍 Performing advanced text analysis...")
            with pdfplumber.open(pdf_path) as pdf:
                text_fields = []
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract all text with positions
                    words = page.extract_words()
                    chars = page.chars
                    
                    print(f"📄 Page {page_num + 1}: {len(words)} words, {len(chars)} characters")
                    
                    # Method 3a: Look for common form patterns
                    form_patterns = [
                        # Common form field labels
                        r'\b(name|full\s*name|first\s*name|last\s*name)\s*:?\s*$',
                        r'\b(email|e-mail|email\s*address)\s*:?\s*$',
                        r'\b(phone|telephone|phone\s*number|tel)\s*:?\s*$',
                        r'\b(address|street\s*address|mailing\s*address)\s*:?\s*$',
                        r'\b(date|date\s*of\s*birth|birth\s*date)\s*:?\s*$',
                        r'\b(signature|sign\s*here|signed\s*by)\s*:?\s*$',
                        r'\b(title|job\s*title|position)\s*:?\s*$',
                        r'\b(company|organization|employer)\s*:?\s*$',
                        r'\b(city|state|zip|postal\s*code)\s*:?\s*$',
                        r'\b(ssn|social\s*security|tax\s*id)\s*:?\s*$',
                        r'\b(id|identification|employee\s*id)\s*:?\s*$',
                        r'\b(department|dept|division)\s*:?\s*$',
                        r'\b(manager|supervisor|approver)\s*:?\s*$',
                        r'\b(notes|comments|remarks)\s*:?\s*$',
                        r'\b(amount|salary|wage|rate)\s*:?\s*$',
                        r'\b(start\s*date|end\s*date|effective\s*date)\s*:?\s*$'
                    ]
                    
                    import re
                    
                    for i, word in enumerate(words):
                        word_text = word['text'].lower()
                        
                        # Check against form patterns
                        for pattern in form_patterns:
                            if re.search(pattern, word_text, re.IGNORECASE):
                                # Look for nearby empty space that could be a field
                                field_x = word['x1'] + 10  # Start field after the label
                                field_y = word['top']
                                field_width = 150
                                field_height = 20
                                
                                # Determine field type based on label
                                if any(keyword in word_text for keyword in ['email', 'e-mail']):
                                    field_type = 'email'
                                elif any(keyword in word_text for keyword in ['date', 'birth']):
                                    field_type = 'date'
                                elif any(keyword in word_text for keyword in ['phone', 'tel']):
                                    field_type = 'tel'
                                elif any(keyword in word_text for keyword in ['signature', 'sign']):
                                    field_type = 'signature'
                                elif any(keyword in word_text for keyword in ['notes', 'comments']):
                                    field_type = 'textarea'
                                else:
                                    field_type = 'text'
                                
                                # Smart assignment
                                if any(keyword in word_text for keyword in ['signature', 'sign', 'manager', 'supervisor', 'approver']):
                                    assigned_to = 'user2'
                                else:
                                    assigned_to = 'user1'
                                
                                text_fields.append({
                                    'id': f'text_p{page_num}_{i}',
                                    'name': word['text'].title(),
                                    'type': field_type,
                                    'value': '',
                                    'position': {'x': field_x, 'y': field_y, 'width': field_width, 'height': field_height},
                                    'assigned_to': assigned_to,
                                    'page': page_num,
                                    'source': 'text_analysis'
                                })
                                break
                    
                    # Method 3b: Look for underscores, lines, or boxes that suggest form fields
                    lines = page.lines if hasattr(page, 'lines') else []
                    rects = page.rects if hasattr(page, 'rects') else []
                    
                    # Detect horizontal lines that might be form fields
                    for line in lines:
                        if line.get('width', 0) > 50 and line.get('height', 1) <= 2:  # Horizontal line
                            text_fields.append({
                                'id': f'line_p{page_num}_{len(text_fields)}',
                                'name': f'Form Field (Line)',
                                'type': 'text',
                                'value': '',
                                'position': {
                                    'x': line.get('x0', 0),
                                    'y': line.get('top', 0) - 5,
                                    'width': line.get('width', 150),
                                    'height': 20
                                },
                                'assigned_to': 'user1',
                                'page': page_num,
                                'source': 'line_detection'
                            })
                    
                    # Detect rectangles that might be form fields
                    for rect in rects:
                        rect_width = rect.get('width', 0)
                        rect_height = rect.get('height', 0)
                        
                        # Look for rectangular areas that look like form fields
                        if 30 < rect_width < 300 and 15 < rect_height < 50:
                            text_fields.append({
                                'id': f'rect_p{page_num}_{len(text_fields)}',
                                'name': f'Form Field (Box)',
                                'type': 'text',
                                'value': '',
                                'position': {
                                    'x': rect.get('x0', 0),
                                    'y': rect.get('top', 0),
                                    'width': rect_width,
                                    'height': rect_height
                                },
                                'assigned_to': 'user1',
                                'page': page_num,
                                'source': 'rect_detection'
                            })
                
                if text_fields:
                    fields.extend(text_fields)
                    print(f"🔍 Added {len(text_fields)} fields from text analysis")
        
        # Method 4: Create intelligent defaults if still no fields found
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

def fill_pdf_fields(pdf_path, field_data, output_path):
    """Fill PDF form fields with provided data"""
    try:
        with open(pdf_path, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Copy pages and fill fields
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # If there are form fields, try to fill them
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        annotation_obj = annotation.get_object()
                        if '/T' in annotation_obj:  # Field name
                            field_name = str(annotation_obj['/T'])
                            if field_name in field_data:
                                annotation_obj.update({
                                    PyPDF2.generic.NameObject('/V'): 
                                    PyPDF2.generic.TextStringObject(field_data[field_name])
                                })
                
                pdf_writer.add_page(page)
            
            # Write the filled PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
                
        return True
        
    except Exception as e:
        print(f"Error filling PDF fields: {e}")
        return False

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
            
            # Add to mock data
            MOCK_DOCUMENTS.append({
                'id': document_id,
                'name': filename,
                'status': 'Awaiting User 2',
                'lastUpdated': 'Just now',
                'created_at': datetime.now().isoformat(),
                'user1_data': user1_data,
                'file_path': file_path,
                'pdf_fields': pdf_analysis['fields'],
                'field_assignments': {field['id']: field['assigned_to'] for field in pdf_analysis['fields']}
            })
            
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
        # Get form data from User 2
        user2_data = {
            'name': request.form.get('user2_name', ''),
            'email': request.form.get('user2_email', ''),
            'manager': request.form.get('manager', ''),
            'hr_rep': request.form.get('hr_rep', ''),
            'benefits': request.form.get('benefits', ''),
            'notes': request.form.get('notes', ''),
            'signature': request.form.get('signature', ''),
            'date_signed': datetime.now().isoformat()
        }
        
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
    document = get_document_by_id(document_id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('dashboard'))
    
    flash('Download functionality requires file storage configuration', 'info')
    return redirect(url_for('dashboard'))

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
    print("🌐 Access at: http://localhost:5002")
    app.run(debug=True, port=5002)