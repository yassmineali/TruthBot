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
            console.log('📤 [API] Uploading file to server...');
            console.log('📤 [API] File name:', file.name);
            console.log('📤 [API] File size:', file.size, 'bytes');
            console.log('📤 [API] File type:', file.type);
            
            const formData = new FormData();
            formData.append('file', file);
            console.log('📤 [API] FormData created');

            const url = `${API_BASE_URL}/analyze/upload`;
            console.log('📤 [API] Sending POST to:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            console.log('📥 [API] Server response status:', response.status);
            console.log('📥 [API] Server response ok:', response.ok);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                console.error('❌ [API] Upload error:', error);
                throw new Error(error.detail || `Upload error: ${response.status}`);
            }

            console.log('📥 [API] Parsing JSON response...');
            const result = await response.json();
            console.log('✅ [API] Upload successful, result:', result);
            console.log('✅ [API] Result label:', result.label);
            console.log('✅ [API] Result confidence:', result.confidence);
            return result;
        } catch (error) {
            console.error('❌ [API] File upload failed:', error);
            console.error('❌ [API] Error name:', error.name);
            console.error('❌ [API] Error message:', error.message);
            console.error('❌ [API] Error stack:', error.stack);
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
    },

    /**
     * Save conversation to database
     * @param {Object} conversationData - Conversation data to save
     * @returns {Promise<Object>} Save result
     */
    async saveConversation(conversationData) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(conversationData)
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Failed to save conversation: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to save conversation:', error);
            throw error;
        }
    },

    /**
     * Get conversation history
     * @param {number} limit - Number of conversations to fetch
     * @param {number} offset - Offset for pagination
     * @param {string} type - Filter by type ('text' or 'file')
     * @returns {Promise<Array>} List of conversations
     */
    async getConversations(limit = 50, offset = 0, type = null) {
        try {
            let url = `${API_BASE_URL}/conversations?limit=${limit}&offset=${offset}`;
            if (type) {
                url += `&type=${type}`;
            }

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Failed to fetch conversations: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
            throw error;
        }
    },

    /**
     * Get conversation statistics
     * @returns {Promise<Object>} Conversation stats
     */
    async getConversationStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/conversations/stats/summary`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `Failed to fetch stats: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to fetch conversation stats:', error);
            throw error;
        }
    }
};
