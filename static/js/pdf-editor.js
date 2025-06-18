class PDFEditor {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            documentId: options.documentId || null,
            userType: options.userType || 'user1',
            enableDragDrop: options.enableDragDrop !== false,
            enableFieldCreation: options.enableFieldCreation !== false,
            ...options
        };
        
        this.fields = [];
        this.selectedField = null;
        this.isDragging = false;
        this.isResizing = false;
        this.dragOffset = { x: 0, y: 0 };
        this.scale = 1;
        
        this.init();
    }
    
    init() {
        this.createEditorHTML();
        this.bindEvents();
        this.loadDocument();
    }
    
    createEditorHTML() {
        this.container.innerHTML = `
            <div class="pdf-editor">
                <div class="pdf-editor-toolbar">
                    <div class="toolbar-section">
                        <button class="btn btn-primary" id="add-text-field">
                            <i class="fas fa-font"></i> Add Text Field
                        </button>
                        <button class="btn btn-primary" id="add-date-field">
                            <i class="fas fa-calendar"></i> Add Date Field
                        </button>
                        <button class="btn btn-primary" id="add-signature-field">
                            <i class="fas fa-signature"></i> Add Signature Field
                        </button>
                        <button class="btn btn-secondary" id="add-checkbox-field">
                            <i class="fas fa-check-square"></i> Add Checkbox
                        </button>
                    </div>
                    <div class="toolbar-section">
                        <label>Zoom: </label>
                        <input type="range" id="zoom-slider" min="50" max="200" value="100" class="form-range">
                        <span id="zoom-display">100%</span>
                    </div>
                    <div class="toolbar-section">
                        <button class="btn btn-success" id="save-fields">
                            <i class="fas fa-save"></i> Save Fields
                        </button>
                        <button class="btn btn-info" id="preview-pdf">
                            <i class="fas fa-eye"></i> Preview
                        </button>
                    </div>
                </div>
                
                <div class="pdf-editor-content">
                    <div class="pdf-viewer-container">
                        <div class="pdf-viewer" id="pdf-viewer">
                            <div class="loading-spinner">
                                <i class="fas fa-spinner fa-spin"></i>
                                Loading PDF...
                            </div>
                        </div>
                        <div class="field-overlay" id="field-overlay"></div>
                    </div>
                    
                    <div class="field-properties-panel" id="field-properties">
                        <h5>Field Properties</h5>
                        <div class="no-selection">
                            Select a field to edit its properties
                        </div>
                        <div class="field-form" style="display: none;">
                            <div class="mb-3">
                                <label class="form-label">Field Name</label>
                                <input type="text" class="form-control" id="field-name">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Field Type</label>
                                <select class="form-select" id="field-type">
                                    <option value="text">Text</option>
                                    <option value="email">Email</option>
                                    <option value="tel">Phone</option>
                                    <option value="date">Date</option>
                                    <option value="textarea">Text Area</option>
                                    <option value="checkbox">Checkbox</option>
                                    <option value="signature">Signature</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Assigned To</label>
                                <select class="form-select" id="field-assignment">
                                    <option value="user1">User 1</option>
                                    <option value="user2">User 2</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Default Value</label>
                                <input type="text" class="form-control" id="field-value">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="field-required">
                                    <label class="form-check-label" for="field-required">
                                        Required Field
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Position & Size</label>
                                <div class="row">
                                    <div class="col-6">
                                        <label class="form-label">X</label>
                                        <input type="number" class="form-control" id="field-x" step="0.1">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label">Y</label>
                                        <input type="number" class="form-control" id="field-y" step="0.1">
                                    </div>
                                </div>
                                <div class="row mt-2">
                                    <div class="col-6">
                                        <label class="form-label">Width</label>
                                        <input type="number" class="form-control" id="field-width" step="0.1">
                                    </div>
                                    <div class="col-6">
                                        <label class="form-label">Height</label>
                                        <input type="number" class="form-control" id="field-height" step="0.1">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <button class="btn btn-danger btn-sm" id="delete-field">
                                    <i class="fas fa-trash"></i> Delete Field
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Toolbar events
        document.getElementById('add-text-field').addEventListener('click', () => this.addField('text'));
        document.getElementById('add-date-field').addEventListener('click', () => this.addField('date'));
        document.getElementById('add-signature-field').addEventListener('click', () => this.addField('signature'));
        document.getElementById('add-checkbox-field').addEventListener('click', () => this.addField('checkbox'));
        
        // Zoom controls
        const zoomSlider = document.getElementById('zoom-slider');
        zoomSlider.addEventListener('input', (e) => this.updateZoom(e.target.value));
        
        // Save and preview
        document.getElementById('save-fields').addEventListener('click', () => this.saveFields());
        document.getElementById('preview-pdf').addEventListener('click', () => this.previewPDF());
        
        // Field properties events
        document.getElementById('field-name').addEventListener('change', (e) => this.updateSelectedField('name', e.target.value));
        document.getElementById('field-type').addEventListener('change', (e) => this.updateSelectedField('type', e.target.value));
        document.getElementById('field-assignment').addEventListener('change', (e) => this.updateSelectedField('assigned_to', e.target.value));
        document.getElementById('field-value').addEventListener('change', (e) => this.updateSelectedField('value', e.target.value));
        document.getElementById('field-required').addEventListener('change', (e) => this.updateSelectedField('is_required', e.target.checked));
        
        // Position controls
        document.getElementById('field-x').addEventListener('change', (e) => this.updateFieldPosition());
        document.getElementById('field-y').addEventListener('change', (e) => this.updateFieldPosition());
        document.getElementById('field-width').addEventListener('change', (e) => this.updateFieldPosition());
        document.getElementById('field-height').addEventListener('change', (e) => this.updateFieldPosition());
        
        // Delete field
        document.getElementById('delete-field').addEventListener('click', () => this.deleteSelectedField());
        
        // Overlay events for drag and drop
        const overlay = document.getElementById('field-overlay');
        overlay.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        overlay.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        overlay.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        overlay.addEventListener('click', (e) => this.handleClick(e));
    }
    
    async loadDocument() {
        if (!this.options.documentId) {
            return;
        }
        
        try {
            // Load PDF fields
            const response = await fetch(`/api/pdf-fields/${this.options.documentId}`);
            const data = await response.json();
            
            if (response.ok) {
                this.fields = data.fields || [];
                this.renderFields();
            }
            
            // Load PDF preview
            await this.loadPDFPreview();
            
        } catch (error) {
            console.error('Error loading document:', error);
            this.showError('Failed to load document');
        }
    }
    
    async loadPDFPreview() {
        try {
            const response = await fetch(`/api/pdf-preview/${this.options.documentId}`);
            const data = await response.json();
            
            if (response.ok && data.preview_url) {
                const viewer = document.getElementById('pdf-viewer');
                viewer.innerHTML = `<img src="${data.preview_url}" alt="PDF Preview" class="pdf-image">`;
                
                // Set up the overlay to match the PDF dimensions
                const img = viewer.querySelector('img');
                img.onload = () => {
                    this.setupOverlay(img.naturalWidth, img.naturalHeight);
                };
            }
        } catch (error) {
            console.error('Error loading PDF preview:', error);
        }
    }
    
    setupOverlay(width, height) {
        const overlay = document.getElementById('field-overlay');
        overlay.style.width = width + 'px';
        overlay.style.height = height + 'px';
        
        this.pdfDimensions = { width, height };
        this.renderFields();
    }
    
    addField(type) {
        const field = {
            id: `field_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name: `New ${type} field`,
            type: type,
            value: '',
            position: {
                x: 100,
                y: 100,
                width: type === 'textarea' ? 300 : 200,
                height: type === 'textarea' ? 80 : 30
            },
            assigned_to: this.options.userType,
            page: 0,
            source: 'user_created',
            is_required: false
        };
        
        this.fields.push(field);
        this.renderFields();
        this.selectField(field);
    }
    
    renderFields() {
        const overlay = document.getElementById('field-overlay');
        overlay.innerHTML = '';
        
        this.fields.forEach(field => {
            const fieldElement = this.createFieldElement(field);
            overlay.appendChild(fieldElement);
        });
    }
    
    createFieldElement(field) {
        const element = document.createElement('div');
        element.className = 'pdf-field';
        element.dataset.fieldId = field.id;
        element.style.cssText = `
            position: absolute;
            left: ${field.position.x * this.scale}px;
            top: ${field.position.y * this.scale}px;
            width: ${field.position.width * this.scale}px;
            height: ${field.position.height * this.scale}px;
            border: 2px solid ${field.assigned_to === 'user1' ? '#007bff' : '#28a745'};
            background: rgba(${field.assigned_to === 'user1' ? '0, 123, 255' : '40, 167, 69'}, 0.1);
            cursor: move;
            box-sizing: border-box;
        `;
        
        // Field label
        const label = document.createElement('div');
        label.className = 'field-label';
        label.textContent = field.name;
        label.style.cssText = `
            position: absolute;
            top: -20px;
            left: 0;
            background: ${field.assigned_to === 'user1' ? '#007bff' : '#28a745'};
            color: white;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
            white-space: nowrap;
        `;
        element.appendChild(label);
        
        // Resize handles
        if (this.options.enableDragDrop) {
            const resizeHandle = document.createElement('div');
            resizeHandle.className = 'resize-handle';
            resizeHandle.style.cssText = `
                position: absolute;
                right: -3px;
                bottom: -3px;
                width: 8px;
                height: 8px;
                background: #333;
                cursor: se-resize;
                border-radius: 2px;
            `;
            element.appendChild(resizeHandle);
        }
        
        return element;
    }
    
    handleMouseDown(e) {
        if (!this.options.enableDragDrop) return;
        
        const fieldElement = e.target.closest('.pdf-field');
        if (!fieldElement) return;
        
        const field = this.getFieldById(fieldElement.dataset.fieldId);
        if (!field) return;
        
        this.selectField(field);
        
        if (e.target.classList.contains('resize-handle')) {
            this.isResizing = true;
            this.isDragging = false;
        } else {
            this.isDragging = true;
            this.isResizing = false;
            
            const rect = fieldElement.getBoundingClientRect();
            const overlayRect = document.getElementById('field-overlay').getBoundingClientRect();
            
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        }
        
        e.preventDefault();
    }
    
    handleMouseMove(e) {
        if (!this.isDragging && !this.isResizing) return;
        if (!this.selectedField) return;
        
        const overlay = document.getElementById('field-overlay');
        const overlayRect = overlay.getBoundingClientRect();
        
        const relativeX = (e.clientX - overlayRect.left) / this.scale;
        const relativeY = (e.clientY - overlayRect.top) / this.scale;
        
        if (this.isDragging) {
            this.selectedField.position.x = Math.max(0, relativeX - this.dragOffset.x / this.scale);
            this.selectedField.position.y = Math.max(0, relativeY - this.dragOffset.y / this.scale);
        } else if (this.isResizing) {
            this.selectedField.position.width = Math.max(50, relativeX - this.selectedField.position.x);
            this.selectedField.position.height = Math.max(20, relativeY - this.selectedField.position.y);
        }
        
        this.renderFields();
        this.updatePropertiesPanel();
        
        e.preventDefault();
    }
    
    handleMouseUp(e) {
        this.isDragging = false;
        this.isResizing = false;
    }
    
    handleClick(e) {
        const fieldElement = e.target.closest('.pdf-field');
        if (fieldElement) {
            const field = this.getFieldById(fieldElement.dataset.fieldId);
            if (field) {
                this.selectField(field);
            }
        } else {
            this.selectField(null);
        }
    }
    
    selectField(field) {
        // Remove previous selection
        document.querySelectorAll('.pdf-field').forEach(el => {
            el.classList.remove('selected');
        });
        
        this.selectedField = field;
        
        if (field) {
            // Highlight selected field
            const fieldElement = document.querySelector(`[data-field-id="${field.id}"]`);
            if (fieldElement) {
                fieldElement.classList.add('selected');
            }
        }
        
        this.updatePropertiesPanel();
    }
    
    updatePropertiesPanel() {
        const noSelection = document.querySelector('.no-selection');
        const fieldForm = document.querySelector('.field-form');
        
        if (!this.selectedField) {
            noSelection.style.display = 'block';
            fieldForm.style.display = 'none';
            return;
        }
        
        noSelection.style.display = 'none';
        fieldForm.style.display = 'block';
        
        // Populate form fields
        document.getElementById('field-name').value = this.selectedField.name || '';
        document.getElementById('field-type').value = this.selectedField.type || 'text';
        document.getElementById('field-assignment').value = this.selectedField.assigned_to || 'user1';
        document.getElementById('field-value').value = this.selectedField.value || '';
        document.getElementById('field-required').checked = this.selectedField.is_required || false;
        
        // Position fields
        document.getElementById('field-x').value = this.selectedField.position.x || 0;
        document.getElementById('field-y').value = this.selectedField.position.y || 0;
        document.getElementById('field-width').value = this.selectedField.position.width || 0;
        document.getElementById('field-height').value = this.selectedField.position.height || 0;
    }
    
    updateSelectedField(property, value) {
        if (!this.selectedField) return;
        
        this.selectedField[property] = value;
        this.renderFields();
    }
    
    updateFieldPosition() {
        if (!this.selectedField) return;
        
        this.selectedField.position.x = parseFloat(document.getElementById('field-x').value) || 0;
        this.selectedField.position.y = parseFloat(document.getElementById('field-y').value) || 0;
        this.selectedField.position.width = parseFloat(document.getElementById('field-width').value) || 0;
        this.selectedField.position.height = parseFloat(document.getElementById('field-height').value) || 0;
        
        this.renderFields();
    }
    
    deleteSelectedField() {
        if (!this.selectedField) return;
        
        const index = this.fields.findIndex(f => f.id === this.selectedField.id);
        if (index > -1) {
            this.fields.splice(index, 1);
            this.selectField(null);
            this.renderFields();
        }
    }
    
    updateZoom(value) {
        this.scale = value / 100;
        document.getElementById('zoom-display').textContent = value + '%';
        
        const viewer = document.getElementById('pdf-viewer');
        const overlay = document.getElementById('field-overlay');
        
        viewer.style.transform = `scale(${this.scale})`;
        overlay.style.transform = `scale(${this.scale})`;
        
        this.renderFields();
    }
    
    async saveFields() {
        if (!this.options.documentId) {
            this.showError('No document ID provided');
            return;
        }
        
        try {
            const response = await fetch(`/api/save-fields/${this.options.documentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fields: this.fields
                })
            });
            
            if (response.ok) {
                this.showSuccess('Fields saved successfully');
            } else {
                throw new Error('Failed to save fields');
            }
        } catch (error) {
            console.error('Error saving fields:', error);
            this.showError('Failed to save fields');
        }
    }
    
    async previewPDF() {
        if (!this.options.documentId) {
            this.showError('No document ID provided');
            return;
        }
        
        // Open preview in new window
        window.open(`/preview/${this.options.documentId}`, '_blank');
    }
    
    getFieldById(id) {
        return this.fields.find(f => f.id === id);
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} notification`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 300px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize PDF Editor when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize if container exists
    const editorContainer = document.getElementById('pdf-editor-container');
    if (editorContainer) {
        const documentId = editorContainer.dataset.documentId;
        const userType = editorContainer.dataset.userType || 'user1';
        
        window.pdfEditor = new PDFEditor('pdf-editor-container', {
            documentId: documentId,
            userType: userType
        });
    }
});