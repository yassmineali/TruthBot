/**
 * TruthBot - API Communication Module
 */

const API_BASE_URL = 'http://localhost:8000/api';

const api = {
    /**
     * Analyze text content
     * @param {string} content - Text to analyze
     * @returns {Promise<Object>} Analysis result
     */
    async analyzeText(content) {
        try {
            const response = await fetch(`${API_BASE_URL}/analyze/text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    file_type: 'text'
                })
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Server error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to server. Please ensure the backend is running.');
            }
            throw error;
        }
    },

    /**
     * Upload and analyze a file
     * @param {File} file - File to analyze
     * @returns {Promise<Object>} Analysis result
     */
    async analyzeFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/analyze/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Upload error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to server. Please ensure the backend is running.');
            }
            throw error;
        }
    },

    /**
     * Check API health
     * @returns {Promise<boolean>} True if healthy
     */
    async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('API not healthy');
            }
            
            return true;
        } catch (error) {
            throw new Error('Cannot connect to the analysis server');
        }
    }
};
