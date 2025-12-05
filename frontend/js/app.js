/**
 * TruthBot - Main Application JavaScript
 */

// DOM Elements
const textInput = document.getElementById('text-input');
const charCounter = document.getElementById('char-counter');
const btnPlus = document.getElementById('btn-plus');
const attachmentMenu = document.getElementById('attachment-menu');
const attachImage = document.getElementById('attach-image');
const attachDocument = document.getElementById('attach-document');
const fileInput = document.getElementById('file-input');
const documentInput = document.getElementById('document-input');
const imagePreviewContainer = document.getElementById('image-preview-container');
const imagePreview = document.getElementById('image-preview');
const imageFilename = document.getElementById('image-filename');
const btnClosePreview = document.getElementById('btn-close-preview');
const documentPreviewContainer = document.getElementById('document-preview-container');
const documentIcon = document.getElementById('document-icon');
const documentFilename = document.getElementById('document-filename');
const documentSize = document.getElementById('document-size');
const btnCloseDocument = document.getElementById('btn-close-document');
const analyzeBtn = document.getElementById('analyze-btn');
const loading = document.getElementById('loading');
const resultSection = document.getElementById('result-section');
const newAnalysisBtn = document.getElementById('new-analysis-btn');
const errorBanner = document.getElementById('error-banner');
const errorMessage = document.getElementById('error-message');

let selectedFile = null;
let selectedFileType = null; // 'image' or 'document'

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTextInput();
    initAttachmentMenu();
    initFileUpload();
    initResults();
    checkApiHealth();
});

// Text Input & Character Counter
function initTextInput() {
    // Character counter
    textInput.addEventListener('input', () => {
        const count = textInput.value.length;
        charCounter.textContent = `${count} character${count !== 1 ? 's' : ''}`;
        updateAnalyzeButton();
    });
}

// Attachment Menu
function initAttachmentMenu() {
    // Toggle menu on plus button click
    btnPlus.addEventListener('click', (e) => {
        e.stopPropagation();
        attachmentMenu.classList.toggle('hidden');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!attachmentMenu.contains(e.target) && !btnPlus.contains(e.target)) {
            attachmentMenu.classList.add('hidden');
        }
    });

    // Image upload
    attachImage.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
        attachmentMenu.classList.add('hidden');
    });

    // Document upload
    attachDocument.addEventListener('click', (e) => {
        e.stopPropagation();
        documentInput.click();
        attachmentMenu.classList.add('hidden');
    });
}

// File Upload
function initFileUpload() {
    // Image file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0], 'image');
        }
    });

    // Document file selection
    documentInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0], 'document');
        }
    });

    // Close preview buttons
    btnClosePreview.addEventListener('click', () => {
        clearFileSelection();
    });

    btnCloseDocument.addEventListener('click', () => {
        clearFileSelection();
    });
}

function handleFileSelection(file, type) {
    // Validate file type
    const imageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
    const documentTypes = ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain'];
    
    if (type === 'image' && !imageTypes.includes(file.type)) {
        const extension = file.name.split('.').pop().toLowerCase();
        if (!['png', 'jpg', 'jpeg', 'gif'].includes(extension)) {
            showError('Please select a valid image file (PNG, JPG, JPEG, GIF)');
            return;
        }
    }
    
    if (type === 'document') {
        const extension = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'doc', 'docx', 'txt'].includes(extension)) {
            showError('Please select a valid document file (PDF, DOC, DOCX, TXT)');
            return;
        }
    }
    
    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 50MB.');
        return;
    }
    
    selectedFile = file;
    selectedFileType = type;
    
    // Show appropriate preview
    if (type === 'image') {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imageFilename.textContent = file.name;
            imagePreviewContainer.classList.remove('hidden');
            documentPreviewContainer.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    } else {
        // Show document preview
        const extension = file.name.split('.').pop().toLowerCase();
        const icons = {
            'pdf': '📕',
            'doc': '📘',
            'docx': '📘',
            'txt': '📄'
        };
        documentIcon.textContent = icons[extension] || '📄';
        documentFilename.textContent = file.name;
        documentSize.textContent = formatFileSize(file.size);
        documentPreviewContainer.classList.remove('hidden');
        imagePreviewContainer.classList.add('hidden');
    }
    
    updateAnalyzeButton();
    hideError();
}

function clearFileSelection() {
    selectedFile = null;
    selectedFileType = null;
    fileInput.value = '';
    documentInput.value = '';
    imagePreviewContainer.classList.add('hidden');
    documentPreviewContainer.classList.add('hidden');
    updateAnalyzeButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateAnalyzeButton() {
    const hasText = textInput.value.trim().length > 0;
    const hasFile = selectedFile !== null;
    analyzeBtn.disabled = !(hasText || hasFile);
}

// Results
function initResults() {
    // New analysis button
    newAnalysisBtn.addEventListener('click', () => {
        hideResults();
        textInput.value = '';
        charCounter.textContent = '0 characters';
        clearFileSelection();
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', async (e) => {
        console.log('🔵 Analyze button clicked');
        e.preventDefault();
        e.stopPropagation();
        console.log('🔵 Event prevented and stopped');
        
        const text = textInput.value.trim();
        console.log('🔵 Text content:', text.substring(0, 50));
        console.log('🔵 Selected file:', selectedFile ? selectedFile.name : 'none');
        
        if (selectedFile) {
            // Analyze file (with optional text)
            console.log('🔵 Starting file analysis...');
            await analyzeContent('file', selectedFile, text);
            console.log('🔵 File analysis completed');
        } else if (text) {
            // Analyze text only
            if (text.length < 10) {
                console.log('⚠️ Text too short:', text.length);
                showError('Please enter at least 10 characters');
                return;
            }
            console.log('🔵 Starting text analysis...');
            await analyzeContent('text', text);
            console.log('🔵 Text analysis completed');
        } else {
            console.log('⚠️ No content to analyze');
            showError('Please enter text or upload a file to analyze');
        }
        console.log('🔵 Analyze button handler finished');
    });
}

// Analyze content
async function analyzeContent(type, content, additionalText = '') {
    console.log('🚀 Starting analysis...', type);
    console.log('🚀 Content:', type === 'text' ? content.substring(0, 50) : content.name);
    
    showLoading(type === 'file' ? 'Uploading and analyzing file...' : 'Analyzing text...');
    console.log('🚀 Loading shown');
    
    hideError();
    hideResults();
    console.log('🚀 UI prepared');
    
    try {
        let result;
        if (type === 'text') {
            console.log('📝 Analyzing text...');
            console.log('📝 Calling api.analyzeText()...');
            result = await api.analyzeText(content);
            console.log('✅ Text analysis complete:', result);
        } else {
            console.log('📁 Uploading file:', content.name, 'Size:', formatFileSize(content.size));
            console.log('📁 Calling api.analyzeFile()...');
            result = await api.analyzeFile(content, additionalText);
            console.log('✅ File analysis complete:', result);
        }
        
        console.log('📊 About to display results...');
        console.log('📊 Result data:', JSON.stringify(result, null, 2));
        displayResults(result);
        
        // Save to conversation history
        console.log('💾 Saving to conversation history...');
        await saveConversation(type, content, result);
        console.log('💾 Conversation saved');
    } catch (error) {
        console.error('❌ Analysis error:', error);
        console.error('❌ Error stack:', error.stack);
        showError(error.message || 'Analysis failed. Please try again.');
    } finally {
        console.log('🏁 Analysis finished, hiding loading...');
        hideLoading();
        console.log('🏁 All done!');
    }
}

// Display results
function displayResults(result) {
    console.log('📊 Displaying results:', result);
    
    // Update result section elements
    const resultLabel = document.getElementById('result-label');
    const resultScore = document.getElementById('result-score');
    const resultBadge = document.getElementById('result-badge');
    const resultExplanation = document.getElementById('result-explanation');
    const resultDetailsList = document.getElementById('result-details-list');
    const resultCard = document.getElementById('result-card');
    
    if (!resultCard) {
        console.error('❌ Result card not found!');
        return;
    }
    
    // Parse result data
    const label = result.label || 'Unknown';
    const confidence = result.confidence || 0;
    const explanation = result.explanation || 'No explanation available.';
    const details = result.details || [];
    
    // Update score/confidence
    if (resultScore) {
        resultScore.textContent = Math.round(confidence * 100) + '%';
    }
    
    // Determine risk level
    const riskLevel = getRiskLevel(label, confidence);
    resultCard.className = 'result-card ' + riskLevel;
    
    // Update badge
    if (resultBadge) {
        const badgeTexts = {
            'risk-low': 'Low Risk',
            'risk-medium': 'Moderate Risk',
            'risk-high': 'High Risk'
        };
        resultBadge.textContent = badgeTexts[riskLevel] || 'Unknown';
    }
    
    // Update explanation
    if (resultExplanation) {
        resultExplanation.textContent = explanation;
    }
    
    // Update details list
    if (resultDetailsList) {
        resultDetailsList.innerHTML = '';
        if (Array.isArray(details) && details.length > 0) {
            details.forEach((item) => {
                const li = document.createElement('li');
                li.textContent = item;
                resultDetailsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Always verify information with multiple reliable sources';
            resultDetailsList.appendChild(li);
        }
    }
    
    // Show results section
    console.log('Showing results section...');
    if (!resultSection) {
        console.error('❌ resultSection not found!');
        return;
    }
    resultSection.classList.remove('hidden');
    console.log('Results section classes:', resultSection.className);
    
    // Scroll to results
    setTimeout(() => {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function getRiskLevel(label, confidence) {
    // Map labels to risk levels
    const labelMap = {
        'reliable': 'risk-low',
        'needs_verification': 'risk-medium',
        'doubtful': 'risk-medium',
        'potentially_false': 'risk-high',
        'false': 'risk-high'
    };
    
    return labelMap[label.toLowerCase()] || 'risk-medium';
}

function formatLabel(label) {
    const labels = {
        'reliable': 'Reliable',
        'doubtful': 'Doubtful',
        'needs_verification': 'Needs Verification',
        'potentially_false': 'Potentially False',
        'unknown': 'Unknown'
    };
    return labels[label] || label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getLabelIcon(label) {
    const icons = {
        'reliable': '✅',
        'doubtful': '⚠️',
        'needs_verification': '🔍',
        'potentially_false': '❌',
        'unknown': '❓'
    };
    return icons[label] || '❓';
}

// Conversation History
async function saveConversation(type, content, result) {
    try {
        const conversationData = {
            type: type,
            content: type === 'text' ? content : null,
            filename: type === 'file' ? content.name : null,
            result: result,
            timestamp: new Date().toISOString()
        };
        
        await api.saveConversation(conversationData);
        console.log('✅ Conversation saved');
    } catch (error) {
        console.error('❌ Failed to save conversation:', error);
        // Don't show error to user, just log it
    }
}

// UI Helpers
function showLoading(message = 'Analyzing...') {
    if (loading) {
        loading.classList.remove('hidden');
        const loadingText = loading.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
    }
}

function hideLoading() {
    if (loading) {
        loading.classList.remove('hidden');
    }
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
    }
}

function hideResults() {
    if (resultSection) {
        resultSection.classList.add('hidden');
    }
}

function showError(message) {
    if (errorMessage && errorBanner) {
        errorMessage.textContent = message;
        errorBanner.classList.remove('hidden');
    }
}

function hideError() {
    if (errorBanner) {
        errorBanner.classList.add('hidden');
    }
}

// Health check
async function checkApiHealth() {
    try {
        await api.checkHealth();
        console.log('✅ API is healthy');
    } catch (error) {
        console.error('❌ API health check failed:', error);
        showError('Cannot connect to the analysis server. Please ensure the backend is running on http://localhost:8000');
    }
}