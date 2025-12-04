/**
 * TruthBot - Main Application JavaScript
 */

// DOM Elements
const textTab = document.getElementById('text-tab');
const fileTab = document.getElementById('file-tab');
const tabBtns = document.querySelectorAll('.tab-btn');
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const analyzeTextBtn = document.getElementById('analyze-text-btn');
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const removeFileBtn = document.getElementById('remove-file-btn');
const analyzeFileBtn = document.getElementById('analyze-file-btn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const newAnalysisBtn = document.getElementById('new-analysis-btn');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');
const toggleDetails = document.getElementById('toggle-details');
const analysisDetailsSection = document.getElementById('analysis-details-section');

let selectedFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initTextInput();
    initFileUpload();
    initResults();
    checkApiHealth();
});

// Tab Switching
function initTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Hide results and errors when switching tabs
            hideResults();
            hideError();
        });
    });
}

// Text Input
function initTextInput() {
    // Character counter
    textInput.addEventListener('input', () => {
        const count = textInput.value.length;
        charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
    });
    
    // Analyze button
    analyzeTextBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        
        if (!text) {
            showError('Please enter some text to analyze');
            return;
        }
        
        if (text.length < 10) {
            showError('Please enter at least 10 characters');
            return;
        }
        
        await analyzeContent('text', text);
    });
}

// File Upload
function initFileUpload() {
    // Click to browse
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });
    
    // Remove file
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFileSelection();
    });
    
    // Analyze file button
    analyzeFileBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            showError('Please select a file first');
            return;
        }
        
        await analyzeContent('file', selectedFile);
    });
}

function handleFileSelection(file) {
    // Validate file type
    const allowedTypes = ['txt', 'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'gif'];
    const extension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(extension)) {
        showError(`File type not supported. Allowed: ${allowedTypes.join(', ')}`);
        return;
    }
    
    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File is too large. Maximum size is 50MB.');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadZone.style.display = 'none';
    fileInfo.classList.add('visible');
    hideError();
}

function clearFileSelection() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.remove('visible');
    uploadZone.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Results
function initResults() {
    // New analysis button
    newAnalysisBtn.addEventListener('click', () => {
        hideResults();
        textInput.value = '';
        charCount.textContent = '0 characters';
        clearFileSelection();
    });
    
    // Toggle details
    if (toggleDetails) {
        toggleDetails.addEventListener('click', () => {
            analysisDetailsSection.classList.toggle('open');
        });
    }
    
    // Retry button
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            hideError();
        });
    }
}

// Analyze content
async function analyzeContent(type, content) {
    showLoading();
    hideError();
    hideResults();
    
    try {
        let result;
        if (type === 'text') {
            result = await api.analyzeText(content);
        } else {
            result = await api.analyzeFile(content);
        }
        
        displayResults(result);
    } catch (error) {
        showError(error.message || 'Analysis failed. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(result) {
    // Update badge
    const badge = document.getElementById('reliability-badge');
    const badgeIcon = document.getElementById('badge-icon');
    const badgeText = document.getElementById('badge-text');
    
    const label = result.label || 'unknown';
    badge.className = 'reliability-badge ' + label.replace(/_/g, '-');
    badgeText.textContent = formatLabel(label);
    badgeIcon.textContent = getLabelIcon(label);
    
    // Update confidence
    const confidenceValue = document.getElementById('confidence-value');
    const confidenceFill = document.getElementById('confidence-fill');
    const confidence = Math.round((result.confidence || 0) * 100);
    confidenceValue.textContent = confidence + '%';
    confidenceFill.style.width = confidence + '%';
    
    // Update content preview
    const contentPreview = document.getElementById('content-preview');
    contentPreview.textContent = result.content_preview || 'No preview available';
    
    // Update reasons
    const reasonsList = document.getElementById('reasons-list');
    reasonsList.innerHTML = '';
    const reasons = result.reasons || [];
    if (reasons.length > 0) {
        reasons.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            reasonsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No specific findings to report';
        reasonsList.appendChild(li);
    }
    
    // Update tips
    const tipsList = document.getElementById('tips-list');
    tipsList.innerHTML = '';
    const tips = result.tips || [];
    if (tips.length > 0) {
        tips.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            tipsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Always verify information with multiple reliable sources';
        tipsList.appendChild(li);
    }
    
    // Update analysis details
    const analysisDetails = document.getElementById('analysis-details');
    if (result.analysis_details) {
        analysisDetails.textContent = result.analysis_details;
        analysisDetailsSection.style.display = 'block';
    } else {
        analysisDetailsSection.style.display = 'none';
    }
    
    // Show results section
    resultsSection.classList.add('visible');
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
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

// UI Helpers
function showLoading() {
    loading.classList.add('visible');
    analyzeTextBtn.disabled = true;
    analyzeFileBtn.disabled = true;
}

function hideLoading() {
    loading.classList.remove('visible');
    analyzeTextBtn.disabled = false;
    analyzeFileBtn.disabled = false;
}

function hideResults() {
    resultsSection.classList.remove('visible');
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.add('visible');
}

function hideError() {
    errorSection.classList.remove('visible');
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