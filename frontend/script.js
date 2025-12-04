document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    const textInput = document.getElementById('text-input');
    const resultCard = document.getElementById('result-card');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorContainer = document.getElementById('error-message');

    // Display elements
    const labelDisplay = document.getElementById('label-display');
    const confidenceDisplay = document.getElementById('confidence-display');
    const reasonsList = document.getElementById('reasons-list');
    const tipDisplay = document.getElementById('tip-display');
    const errorText = document.getElementById('error-text');
    
    // The backend API URL (M1 will confirm this)
    const API_ENDPOINT = '/analyze'; 
    // IMPORTANT: For local testing, you might need 'http://localhost:8000/analyze' 

    // Function to hide all dynamic elements
    function resetView() {
        resultCard.classList.add('hidden');
        loadingIndicator.classList.add('hidden');
        errorContainer.classList.add('hidden');
        analyzeButton.disabled = false;
        // Remove all label classes from the card
        resultCard.className = 'result-card hidden';
    }

    analyzeButton.addEventListener('click', async () => {
        resetView();
        const text = textInput.value.trim();

        if (text.length === 0) {
            alert("Please enter some text to analyze.");
            return;
        }

        analyzeButton.disabled = true;
        loadingIndicator.classList.remove('hidden');

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            loadingIndicator.classList.add('hidden');

            if (!response.ok) {
                // If M1's API returns an error (4xx or 5xx)
                throw new Error(`Server returned status: ${response.status}`);
            }

            const data = await response.json();
            
            // --- M3 CORE LOGIC: Displaying the result ---
            
            const labelKey = data.label.toLowerCase().replace(/[^a-z0-9]/g, '-');
            
            labelDisplay.textContent = data.label;
            confidenceDisplay.textContent = `${Math.round(data.confidence * 100)}%`;
            tipDisplay.textContent = data.tip;
            
            // Clear and populate reasons list
            reasonsList.innerHTML = '';
            data.reasons.forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                reasonsList.appendChild(li);
            });

            // Apply the style based on the label (M4's definitions)
            resultCard.classList.remove('hidden');
            resultCard.classList.add(labelKey);
            
        } catch (error) {
            loadingIndicator.classList.add('hidden');
            errorContainer.classList.remove('hidden');
            errorText.textContent = `Could not analyze content. Error details: ${error.message}. Please check with the Backend Integrator (M1).`;
            console.error('Analysis failed:', error);
        } finally {
            analyzeButton.disabled = false;
        }
    });
});