/**
 * Real-Time PDF Editor
 * Handles PDF rendering, field overlay, and real-time collaboration
 */

class RealtimePDFEditor {
    constructor(options) {
        this.documentId = options.documentId;
        this.socketUrl = options.socketUrl;
        this.apiBaseUrl = options.apiBaseUrl;
        
        // State
        this.currentPage = 1;
        this.totalPages = 1;
        this.zoomLevel = 1.0;
        this.pdfDocument = null;
        this.fields = new Map();
        this.selectedField = null;
        this.isConnected = false;
        this.sessionId = this.generateSessionId();
        
        // Elements
        this.elements = {};
        this.initializeElements();
        
        // Socket connection
        this.socket = null;
        this.initializeSocket();
        
        // Event listeners
        this.initializeEventListeners();
        
        // Load PDF if document ID is provided
        if (this.documentId) {
            this.loadDocument();
        }
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeElements() {
        this.elements = {
            // Header elements
            documentName: document.getElementById('documentName'),
            connectionStatus: document.getElementById('connectionStatus'),
            statusText: document.getElementById('statusText'),
            zoomLevel: document.getElementById('zoomLevel'),
            pageInfo: document.getElementById('pageInfo'),
            
            // Controls
            zoomIn: document.getElementById('zoomIn'),
            zoomOut: document.getElementById('zoomOut'),
            prevPage: document.getElementById('prevPage'),
            nextPage: document.getElementById('nextPage'),
            saveBtn: document.getElementById('saveBtn'),
            downloadBtn: document.getElementById('downloadBtn'),
            
            // PDF viewer
            pdfViewer: document.getElementById('pdfViewer'),
            fieldOverlay: document.getElementById('fieldOverlay'),
            
            // Sidebar
            fieldsList: document.getElementById('fieldsList'),
            fieldProperties: document.getElementById('fieldProperties'),
            activeUsers: document.getElementById('activeUsers'),
            
            // Modals
            uploadModal: document.getElementById('uploadModal'),
            fieldEditModal: document.getElementById('fieldEditModal'),
            pdfFileInput: document.getElementById('pdfFileInput'),
            uploadArea: document.getElementById('uploadArea'),
            uploadProgress: document.getElementById('uploadProgress'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText')
        };
    }
    
    initializeSocket() {
        this.socket = io(this.socketUrl, {
            query: {
                documentId: this.documentId,
                sessionId: this.sessionId
            }
        });
        
        this.socket.on('connect', () => {
            console.log('Connected to real-time server');
            this.isConnected = true;
            this.updateConnectionStatus();
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from real-time server');
            this.isConnected = false;
            this.updateConnectionStatus();
        });
        
        this.socket.on('field_updated', (data) => {
            this.handleFieldUpdate(data);
        });
        
        this.socket.on('user_joined', (data) => {
            this.handleUserJoined(data);
        });
        
        this.socket.on('user_left', (data) => {
            this.handleUserLeft(data);
        });
        
        this.socket.on('field_focus', (data) => {
            this.handleFieldFocus(data);
        });
    }
    
    initializeEventListeners() {
        // Zoom controls
        this.elements.zoomIn.addEventListener('click', () => this.zoomIn());
        this.elements.zoomOut.addEventListener('click', () => this.zoomOut());
        
        // Page controls
        this.elements.prevPage.addEventListener('click', () => this.previousPage());
        this.elements.nextPage.addEventListener('click', () => this.nextPage());
        
        // Save and download
        this.elements.saveBtn.addEventListener('click', () => this.saveDocument());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadPDF());
        
        // File upload
        this.elements.pdfFileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        this.setupDragAndDrop();
        
        // PDF viewer interactions
        this.elements.pdfViewer.addEventListener('click', (e) => this.handlePDFClick(e));
        this.elements.fieldOverlay.addEventListener('click', (e) => this.handleFieldClick(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    updateConnectionStatus() {
        const statusDot = this.elements.connectionStatus;
        const statusText = this.elements.statusText;
        
        if (this.isConnected) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Disconnected';
        }
    }
    
    async loadDocument() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/documents/${this.documentId}`);
            const document = await response.json();
            
            this.elements.documentName.textContent = document.name;
            
            // Load PDF from preview endpoint
            const pdfUrl = `${this.apiBaseUrl}/documents/${this.documentId}/preview`;
            await this.loadPDF(pdfUrl);
            
            // Load fields
            await this.loadFields();
            
        } catch (error) {
            console.error('Error loading document:', error);
            this.showError('Failed to load document');
        }
    }
    
    async loadPDF(pdfPath) {
        try {
            // Configure PDF.js worker
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            
            // Load PDF
            const loadingTask = pdfjsLib.getDocument(pdfPath);
            this.pdfDocument = await loadingTask.promise;
            
            this.totalPages = this.pdfDocument.numPages;
            this.updatePageInfo();
            
            // Render first page
            await this.renderPage(1);
            
            // Hide loading indicator
            this.elements.pdfViewer.querySelector('.pdf-loading').style.display = 'none';
            
        } catch (error) {
            console.error('Error loading PDF:', error);
            this.showError('Failed to load PDF');
        }
    }
    
    async renderPage(pageNumber) {
        try {
            const page = await this.pdfDocument.getPage(pageNumber);
            
            // Calculate scale based on zoom level
            const viewport = page.getViewport({ scale: this.zoomLevel });
            
            // Create canvas
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            
            // Create page container
            const pageContainer = document.createElement('div');
            pageContainer.className = 'pdf-page';
            pageContainer.dataset.pageNumber = pageNumber;
            pageContainer.appendChild(canvas);
            
            // Clear existing pages and add new one
            const existingPages = this.elements.pdfViewer.querySelectorAll('.pdf-page');
            existingPages.forEach(page => page.remove());
            this.elements.pdfViewer.appendChild(pageContainer);
            
            // Render PDF page
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };
            
            await page.render(renderContext).promise;
            
            // Update field overlay
            this.updateFieldOverlay();
            
        } catch (error) {
            console.error('Error rendering page:', error);
        }
    }
    
    async loadFields() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/documents/${this.documentId}/fields`);
            const fields = await response.json();
            
            this.fields.clear();
            fields.forEach(field => {
                this.fields.set(field.id, field);
            });
            
            this.updateFieldsList();
            this.updateFieldOverlay();
            
        } catch (error) {
            console.error('Error loading fields:', error);
        }
    }
    
    updateFieldsList() {
        const fieldsList = this.elements.fieldsList;
        fieldsList.innerHTML = '';
        
        this.fields.forEach(field => {
            const fieldItem = document.createElement('div');
            fieldItem.className = 'field-item';
            fieldItem.dataset.fieldId = field.id;
            
            fieldItem.innerHTML = `
                <div class="field-name">${field.name}</div>
                <div class="field-type">${field.type}</div>
                ${field.value ? `<div class="field-value">${field.value}</div>` : ''}
            `;
            
            fieldItem.addEventListener('click', () => this.selectField(field.id));
            fieldItem.addEventListener('dblclick', () => openFieldEditModal(field.id));
            fieldsList.appendChild(fieldItem);
        });
    }
    
    updateFieldOverlay() {
        const overlay = this.elements.fieldOverlay;
        overlay.innerHTML = '';
        
        const pageContainer = this.elements.pdfViewer.querySelector('.pdf-page');
        if (!pageContainer) return;
        
        const pageRect = pageContainer.getBoundingClientRect();
        const viewerRect = this.elements.pdfViewer.getBoundingClientRect();
        
        this.fields.forEach(field => {
            if (field.position && field.position.page === this.currentPage) {
                const fieldElement = this.createFieldElement(field, pageRect, viewerRect);
                overlay.appendChild(fieldElement);
            }
        });
    }
    
    createFieldElement(field, pageRect, viewerRect) {
        const fieldElement = document.createElement('div');
        fieldElement.className = 'overlay-field';
        fieldElement.dataset.fieldId = field.id;
        
        // Calculate position relative to the viewer
        const x = pageRect.left - viewerRect.left + (field.position.x * this.zoomLevel);
        const y = pageRect.top - viewerRect.top + (field.position.y * this.zoomLevel);
        const width = field.position.width * this.zoomLevel;
        const height = field.position.height * this.zoomLevel;
        
        fieldElement.style.left = `${x}px`;
        fieldElement.style.top = `${y}px`;
        fieldElement.style.width = `${width}px`;
        fieldElement.style.height = `${height}px`;
        
        // Create input element based on field type
        let inputElement;
        switch (field.type) {
            case 'text':
            case 'email':
            case 'tel':
                inputElement = document.createElement('input');
                inputElement.type = field.type;
                inputElement.value = field.value || '';
                inputElement.className = 'field-input';
                break;
                
            case 'checkbox':
                inputElement = document.createElement('input');
                inputElement.type = 'checkbox';
                inputElement.checked = field.value === 'true';
                inputElement.className = 'field-checkbox';
                break;
                
            case 'date':
                inputElement = document.createElement('input');
                inputElement.type = 'date';
                inputElement.value = field.value || '';
                inputElement.className = 'field-input';
                break;
                
            case 'signature':
                inputElement = document.createElement('div');
                inputElement.className = 'field-signature';
                inputElement.textContent = field.value || 'Click to sign';
                break;
                
            default:
                inputElement = document.createElement('input');
                inputElement.type = 'text';
                inputElement.value = field.value || '';
                inputElement.className = 'field-input';
        }
        
        // Add event listeners
        inputElement.addEventListener('input', (e) => {
            this.updateFieldValue(field.id, e.target.value);
        });
        
        inputElement.addEventListener('focus', () => {
            this.focusField(field.id);
        });
        
        inputElement.addEventListener('blur', () => {
            this.blurField(field.id);
        });
        
        fieldElement.appendChild(inputElement);
        return fieldElement;
    }
    
    selectField(fieldId) {
        // Remove previous selection
        document.querySelectorAll('.field-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        document.querySelectorAll('.overlay-field.selected').forEach(field => {
            field.classList.remove('selected');
        });
        
        // Add selection to new field
        const fieldItem = document.querySelector(`[data-field-id="${fieldId}"]`);
        if (fieldItem) {
            fieldItem.classList.add('selected');
        }
        
        const overlayField = this.elements.fieldOverlay.querySelector(`[data-field-id="${fieldId}"]`);
        if (overlayField) {
            overlayField.classList.add('selected');
        }
        
        this.selectedField = fieldId;
        this.updateFieldProperties();
    }
    
    updateFieldProperties() {
        const propertiesPanel = this.elements.fieldProperties;
        
        if (!this.selectedField) {
            propertiesPanel.innerHTML = '<p class="no-selection">Select a field to edit properties</p>';
            return;
        }
        
        const field = this.fields.get(this.selectedField);
        if (!field) return;
        
        propertiesPanel.innerHTML = `
            <div class="property-group">
                <label>Name:</label>
                <input type="text" value="${field.name}" onchange="pdfEditor.updateFieldProperty('name', this.value)">
            </div>
            <div class="property-group">
                <label>Type:</label>
                <select onchange="pdfEditor.updateFieldProperty('type', this.value)">
                    <option value="text" ${field.type === 'text' ? 'selected' : ''}>Text</option>
                    <option value="email" ${field.type === 'email' ? 'selected' : ''}>Email</option>
                    <option value="tel" ${field.type === 'tel' ? 'selected' : ''}>Phone</option>
                    <option value="date" ${field.type === 'date' ? 'selected' : ''}>Date</option>
                    <option value="checkbox" ${field.type === 'checkbox' ? 'selected' : ''}>Checkbox</option>
                    <option value="signature" ${field.type === 'signature' ? 'selected' : ''}>Signature</option>
                </select>
            </div>
            <div class="property-group">
                <label>Value:</label>
                <input type="text" value="${field.value || ''}" onchange="pdfEditor.updateFieldProperty('value', this.value)">
            </div>
            <div class="property-group">
                <label>
                    <input type="checkbox" ${field.required ? 'checked' : ''} onchange="pdfEditor.updateFieldProperty('required', this.checked)">
                    Required
                </label>
            </div>
            <div class="property-group">
                <label>Assigned to:</label>
                <select onchange="pdfEditor.updateFieldProperty('assigned_to', this.value)">
                    <option value="user1" ${field.assigned_to === 'user1' ? 'selected' : ''}>User 1</option>
                    <option value="user2" ${field.assigned_to === 'user2' ? 'selected' : ''}>User 2</option>
                    <option value="admin" ${field.assigned_to === 'admin' ? 'selected' : ''}>Admin</option>
                </select>
            </div>
        `;
    }
    
    updateFieldProperty(property, value) {
        console.log('updateFieldProperty called:', {property, value, selectedField: this.selectedField});
        
        if (!this.selectedField) {
            console.warn('No field selected');
            return;
        }
        
        const field = this.fields.get(this.selectedField);
        if (!field) {
            console.warn('Field not found:', this.selectedField);
            return;
        }
        
        console.log('Updating field:', field.name, 'property:', property, 'from:', field[property], 'to:', value);
        
        // Update field locally
        field[property] = value;
        field.updated_at = new Date().toISOString();
        this.fields.set(this.selectedField, field);
        
        // Send update to server if socket is connected
        if (this.socket && this.socket.connected) {
            this.socket.emit('field_update', {
                fieldId: this.selectedField,
                property: property,
                value: value,
                sessionId: this.sessionId
            });
            console.log('Sent field update to server');
        } else {
            console.warn('Socket not connected, update not sent to server');
        }
        
        // Update UI immediately
        this.updateFieldsList();
        this.updateFieldOverlay();
        
        // Update properties panel if it's the selected field
        if (this.selectedField) {
            this.updateFieldProperties();
        }
        
        // Show feedback
        showNotification(`Updated ${property}: ${value}`, 'success');
    }
    
    updateFieldValue(fieldId, value) {
        const field = this.fields.get(fieldId);
        if (!field) return;
        
        field.value = value;
        field.updated_at = new Date().toISOString();
        this.fields.set(fieldId, field);
        
        // Send real-time update
        this.socket.emit('field_update', {
            fieldId: fieldId,
            property: 'value',
            value: value,
            sessionId: this.sessionId
        });
        
        // Update field list
        this.updateFieldsList();
    }
    
    focusField(fieldId) {
        this.socket.emit('field_focus', {
            fieldId: fieldId,
            sessionId: this.sessionId,
            action: 'focus'
        });
        
        const overlayField = this.elements.fieldOverlay.querySelector(`[data-field-id="${fieldId}"]`);
        if (overlayField) {
            overlayField.classList.add('editing');
        }
    }
    
    blurField(fieldId) {
        this.socket.emit('field_focus', {
            fieldId: fieldId,
            sessionId: this.sessionId,
            action: 'blur'
        });
        
        const overlayField = this.elements.fieldOverlay.querySelector(`[data-field-id="${fieldId}"]`);
        if (overlayField) {
            overlayField.classList.remove('editing');
        }
    }
    
    // Event handlers
    handleFieldUpdate(data) {
        if (data.sessionId === this.sessionId) return; // Ignore own updates
        
        const field = this.fields.get(data.fieldId);
        if (field) {
            field[data.property] = data.value;
            this.fields.set(data.fieldId, field);
            
            // Update UI
            this.updateFieldsList();
            this.updateFieldOverlay();
            
            if (this.selectedField === data.fieldId) {
                this.updateFieldProperties();
            }
        }
    }
    
    handleFieldFocus(data) {
        if (data.sessionId === this.sessionId) return;
        
        const overlayField = this.elements.fieldOverlay.querySelector(`[data-field-id="${data.fieldId}"]`);
        if (overlayField) {
            if (data.action === 'focus') {
                overlayField.classList.add('editing');
            } else {
                overlayField.classList.remove('editing');
            }
        }
    }
    
    handleUserJoined(data) {
        console.log('User joined:', data);
        this.updateActiveUsers();
    }
    
    handleUserLeft(data) {
        console.log('User left:', data);
        this.updateActiveUsers();
    }
    
    updateActiveUsers() {
        // This would typically fetch active users from the server
        // For now, just show a placeholder
        this.elements.activeUsers.innerHTML = `
            <div class="user-avatar">
                <div class="user-dot"></div>
                <span class="user-name">You</span>
            </div>
        `;
    }
    
    // Navigation
    zoomIn() {
        this.zoomLevel = Math.min(this.zoomLevel * 1.2, 3.0);
        this.updateZoom();
    }
    
    zoomOut() {
        this.zoomLevel = Math.max(this.zoomLevel / 1.2, 0.5);
        this.updateZoom();
    }
    
    updateZoom() {
        this.elements.zoomLevel.textContent = `${Math.round(this.zoomLevel * 100)}%`;
        this.renderPage(this.currentPage);
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.updatePageInfo();
            this.renderPage(this.currentPage);
        }
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            this.updatePageInfo();
            this.renderPage(this.currentPage);
        }
    }
    
    updatePageInfo() {
        this.elements.pageInfo.textContent = `Page ${this.currentPage} of ${this.totalPages}`;
        this.elements.prevPage.disabled = this.currentPage === 1;
        this.elements.nextPage.disabled = this.currentPage === this.totalPages;
    }
    
    // File upload
    setupDragAndDrop() {
        const uploadArea = this.elements.uploadArea;
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });
        
        uploadArea.addEventListener('click', () => {
            this.elements.pdfFileInput.click();
        });
    }
    
    handleFileUpload(e) {
        const file = e.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }
    
    async uploadFile(file) {
        if (file.type !== 'application/pdf') {
            this.showError('Please select a PDF file');
            return;
        }
        
        const formData = new FormData();
        formData.append('pdf', file);
        
        // Show progress
        this.elements.uploadProgress.style.display = 'block';
        this.elements.progressText.textContent = 'Uploading...';
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/documents/upload`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.documentId = result.document.id;
                this.elements.uploadModal.style.display = 'none';
                await this.loadDocument();
            } else {
                this.showError(result.message || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Upload failed');
        } finally {
            this.elements.uploadProgress.style.display = 'none';
        }
    }
    
    // Save and download
    async saveDocument() {
        try {
            const fieldsData = Array.from(this.fields.values());
            
            const response = await fetch(`${this.apiBaseUrl}/documents/${this.documentId}/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fields: fieldsData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Document saved successfully');
            } else {
                this.showError(result.message || 'Save failed');
            }
            
        } catch (error) {
            console.error('Save error:', error);
            this.showError('Save failed');
        }
    }
    
    async downloadPDF() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/documents/${this.documentId}/download`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.documentId}.pdf`;
                a.click();
                URL.revokeObjectURL(url);
            } else {
                this.showError('Download failed');
            }
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Download failed');
        }
    }
    
    // Utility methods
    showError(message) {
        // Simple alert for now - could be enhanced with toast notifications
        alert('Error: ' + message);
    }
    
    showSuccess(message) {
        // Simple alert for now - could be enhanced with toast notifications
        alert('Success: ' + message);
    }
    
    handleResize() {
        if (this.pdfDocument) {
            this.updateFieldOverlay();
        }
    }
    
    handleKeyDown(e) {
        // Keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    this.saveDocument();
                    break;
                case '=':
                case '+':
                    e.preventDefault();
                    this.zoomIn();
                    break;
                case '-':
                    e.preventDefault();
                    this.zoomOut();
                    break;
            }
        }
    }
}

// Global instance
let pdfEditor;

// Modal functions
function closeFieldEditModal() {
    const modal = document.getElementById('fieldEditModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openFieldEditModal(fieldId) {
    const modal = document.getElementById('fieldEditModal');
    if (!modal || !pdfEditor) return;
    
    const field = pdfEditor.fields.get(fieldId);
    if (!field) return;
    
    // Populate modal with field data
    document.getElementById('fieldName').value = field.name || '';
    document.getElementById('fieldType').value = field.type || 'text';
    document.getElementById('fieldValue').value = field.value || '';
    document.getElementById('fieldRequired').checked = field.required || false;
    document.getElementById('fieldAssignedTo').value = field.assigned_to || 'user1';
    
    // Store current field ID for saving
    modal.dataset.fieldId = fieldId;
    
    // Show modal
    modal.style.display = 'block';
}

function saveFieldChanges() {
    console.log('saveFieldChanges called');
    
    const modal = document.getElementById('fieldEditModal');
    if (!modal) {
        console.error('Modal not found');
        return;
    }
    
    if (!pdfEditor) {
        console.error('pdfEditor not initialized');
        showNotification('Editor not ready', 'error');
        return;
    }
    
    const fieldId = modal.dataset.fieldId;
    if (!fieldId) {
        console.error('No field ID found in modal');
        showNotification('No field selected', 'error');
        return;
    }
    
    // Get form values
    const name = document.getElementById('fieldName').value;
    const type = document.getElementById('fieldType').value;
    const value = document.getElementById('fieldValue').value;
    const required = document.getElementById('fieldRequired').checked;
    const assignedTo = document.getElementById('fieldAssignedTo').value;
    
    console.log('Saving field changes:', {fieldId, name, type, value, required, assignedTo});
    
    // Select the field first
    pdfEditor.selectField(fieldId);
    
    // Update field properties one by one
    try {
        if (name && name !== pdfEditor.fields.get(fieldId)?.name) {
            pdfEditor.updateFieldProperty('name', name);
        }
        if (type && type !== pdfEditor.fields.get(fieldId)?.type) {
            pdfEditor.updateFieldProperty('type', type);
        }
        if (value !== pdfEditor.fields.get(fieldId)?.value) {
            pdfEditor.updateFieldProperty('value', value);
        }
        if (required !== pdfEditor.fields.get(fieldId)?.required) {
            pdfEditor.updateFieldProperty('required', required);
        }
        if (assignedTo && assignedTo !== pdfEditor.fields.get(fieldId)?.assigned_to) {
            pdfEditor.updateFieldProperty('assigned_to', assignedTo);
        }
        
        // Close modal
        closeFieldEditModal();
        
        // Show success message
        showNotification('Field updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error saving field changes:', error);
        showNotification('Error saving changes: ' + error.message, 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 3000;
        font-size: 14px;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}