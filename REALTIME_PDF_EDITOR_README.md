# 📄 Real-Time PDF Editor

A comprehensive web-based PDF editor that allows users to upload PDF documents, edit form fields directly in the browser with real-time collaboration, and generate updated PDFs with all changes applied.

## ✨ Features

### 🎯 Core Features
- **Real-time PDF preview** with interactive field overlay
- **Live collaborative editing** with WebSocket synchronization
- **Accurate field detection** and position extraction from uploaded PDFs
- **Real-time PDF generation** with live field values
- **Database persistence** for field configurations and user sessions
- **Multi-user collaboration** with live cursor tracking

### 📝 Field Types Supported
- **Text Fields**: Single-line text input
- **Email Fields**: Email validation and formatting
- **Phone Fields**: Phone number input with formatting
- **Date Fields**: Date picker and validation
- **Checkboxes**: Boolean selection with visual indicators
- **Radio Buttons**: Single selection from groups
- **Signature Fields**: Digital signature capture and display

### 🔧 Technical Features
- **Accurate positioning** with relative and absolute coordinates
- **Real-time synchronization** across multiple users
- **Field validation** and data sanitization
- **PDF flattening** for permanent content embedding
- **Preview generation** with base64 image encoding
- **Session management** with activity tracking
- **Audit logging** for all field changes

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# The app will automatically create tables on first run
# Make sure your Supabase/PostgreSQL database is accessible
```

### 3. Start the Server

```bash
python app.py
```

### 4. Access the Editor

Open your browser to:
- **Main app**: http://localhost:5006
- **Real-time editor**: http://localhost:5006/realtime-editor

## 📋 Usage Guide

### Uploading a PDF

1. **Open the real-time editor** at `/realtime-editor`
2. **Click "Choose PDF File"** or drag & drop a PDF
3. **Wait for processing** - the system will:
   - Extract PDF information and dimensions
   - Detect all form fields and their positions
   - Create interactive field overlays
   - Set up real-time collaboration

### Editing Fields

1. **Click on any field** in the PDF preview to select it
2. **Edit field properties** in the sidebar:
   - Change field name and type
   - Set required status
   - Assign to users
   - Modify styling
3. **Enter field values** directly in the overlay inputs
4. **See changes instantly** synchronized across all connected users

### Real-time Collaboration

- **Multiple users** can edit the same document simultaneously
- **Live cursor tracking** shows where others are editing
- **Instant synchronization** of all field changes
- **Session management** tracks active users
- **Conflict resolution** ensures data consistency

### Downloading Results

1. **Click "Save"** to persist all changes to the database
2. **Click "Download PDF"** to generate and download the filled PDF
3. **All field values** are permanently embedded in the output PDF
4. **Content is flattened** and visible in any PDF viewer

## 🏗️ Architecture

### Frontend Components

```
realtime_pdf_editor.html     # Main editor interface
realtime-editor.css          # Styling and responsive design
realtime-pdf-editor.js       # JavaScript controller
```

### Backend Components

```
realtime_routes.py           # Flask routes and WebSocket handlers
realtime_pdf_processor.py    # Enhanced PDF processing
models.py                    # Database models with real-time support
```

### Key Classes

- **`RealtimePDFEditor`**: Frontend JavaScript controller
- **`RealtimePDFProcessor`**: Backend PDF processing engine
- **`PDFConfiguration`**: Database model for PDF settings
- **`RealTimeSession`**: Session tracking for collaboration

## 🗄️ Database Schema

### Core Tables

```sql
-- Documents with PDF metadata
documents (id, name, file_path, status, created_at, metadata)

-- Individual form fields with positions
document_fields (id, document_id, name, type, value, position, styling)

-- PDF configuration and rendering settings
pdf_configurations (id, document_id, pdf_info, field_mapping)

-- Real-time session tracking
realtime_sessions (id, document_id, user_id, session_data, is_active)

-- Audit log for all changes
audit_logs (id, document_id, field_id, action, old_value, new_value)
```

### Field Position Structure

```json
{
  "x": 100,           // Absolute X coordinate
  "y": 200,           // Absolute Y coordinate  
  "width": 150,       // Field width
  "height": 25,       // Field height
  "page": 1,          // Page number (1-indexed)
  "page_width": 612,  // PDF page width
  "page_height": 792, // PDF page height
  "relative_x": 0.16, // Relative X (0-1)
  "relative_y": 0.25  // Relative Y (0-1)
}
```

## 🔌 API Endpoints

### Document Management

```http
POST /realtime/api/documents/upload
GET  /realtime/api/documents/{id}
GET  /realtime/api/documents/{id}/fields
POST /realtime/api/documents/{id}/save
GET  /realtime/api/documents/{id}/download
GET  /realtime/api/documents/{id}/preview
```

### WebSocket Events

```javascript
// Client to Server
socket.emit('field_update', {fieldId, property, value, sessionId})
socket.emit('field_focus', {fieldId, sessionId, action})
socket.emit('request_document_state', {documentId, sessionId})

// Server to Client
socket.on('field_updated', {fieldId, property, value, sessionId})
socket.on('field_focus', {fieldId, sessionId, action})
socket.on('user_joined', {sessionId, documentId})
socket.on('user_left', {sessionId, documentId})
socket.on('document_state', {documentId, fields})
```

## 📊 Field Detection Algorithm

The system uses a multi-layered approach to detect PDF form fields:

### 1. Widget Analysis
- Extracts native PDF form widgets using PyMuPDF
- Determines field types from PDF field codes
- Calculates accurate positions and dimensions

### 2. Text Analysis
- Searches for signature-related text patterns
- Creates signature fields near detected text
- Handles forms without native widgets

### 3. Visual Analysis
- Detects horizontal lines for signature areas
- Identifies potential form regions
- Creates intelligent field mappings

### 4. Smart Assignment
- Assigns fields to users based on position and name
- Right-side fields typically assigned to "user2"
- Signature fields assigned to secondary user
- Maintains compatibility with existing workflows

## 🎨 Styling and Appearance

### Field Styling Structure

```json
{
  "font_size": 12,
  "font_family": "Arial",
  "color": "#000000",
  "background_color": "#ffffff", 
  "border_color": "#cccccc",
  "border_width": 1,
  "text_align": "left"
}
```

### Visual Indicators

- **Blue border**: Selected field
- **Green border**: Currently being edited
- **Checkmarks**: Filled checkboxes
- **Dots**: Selected radio buttons
- **Signature areas**: Light yellow background

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DB_HOST=your-supabase-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=postgres
DB_PORT=5432

# Supabase API (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=true
```

### Upload Configuration

```python
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf'}
```

## 🧪 Testing

### Run the Test Suite

```bash
python test_realtime_editor.py
```

### Test Coverage

- ✅ PDF information extraction
- ✅ Field detection and positioning
- ✅ Real-time PDF filling
- ✅ Field data validation
- ✅ Preview generation
- ✅ Database operations
- ✅ WebSocket communication

## 🚨 Troubleshooting

### Common Issues

**PDF fields not detected**
- Ensure PDF has actual form fields (not just fillable areas)
- Check PDF is not password protected
- Verify PDF is not corrupted

**Real-time sync not working**
- Check WebSocket connection in browser console
- Verify SocketIO dependencies are installed
- Ensure firewall allows WebSocket connections

**Field positions incorrect**
- Check PDF page dimensions match expectations
- Verify zoom level is set correctly
- Test with different PDF viewers

**Database connection failed**
- Verify database credentials in .env file
- Check database server is accessible
- Ensure PostgreSQL/Supabase is running

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-page editing** with page navigation
- **Advanced signature capture** with drawing pad
- **Field validation rules** and custom constraints
- **Template management** for reusable forms
- **Version history** and change tracking
- **Advanced collaboration** with user permissions
- **Mobile responsive** design improvements
- **Offline editing** with synchronization

### Integration Possibilities
- **Document management systems**
- **Workflow automation platforms**
- **Digital signature services**
- **Cloud storage providers**
- **Notification systems**

## 📄 License

This project is part of the PDF Collaborator application and follows the same licensing terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review the test suite for examples
- Examine the browser console for errors
- Check server logs for backend issues

---

**Built with ❤️ using Flask, SocketIO, PyMuPDF, and modern web technologies**