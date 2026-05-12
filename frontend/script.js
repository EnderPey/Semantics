const analyzeBtn = document.getElementById('analyzeBtn');
const textInput = document.getElementById('textInput');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');
const resultsSection = document.getElementById('resultsSection');
const llmAnalysis = document.getElementById('llmAnalysis');

let sentimentChartInstance = null;
let entropyChartInstance = null;

// Chart.js default theme configuration for dark mode
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

analyzeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) return alert("Please enter some text to analyze.");

    // UI Loading state
    btnText.textContent = "Analyzing...";
    loader.classList.remove('hidden');
    analyzeBtn.disabled = true;
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        // Render data
        renderSynthesis(data.analysis);
        renderCharts(data.segments, data.sentiment, data.entropy);
        
        // Show results
        resultsSection.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        alert("An error occurred during analysis. Make sure the backend is running.");
    } finally {
        // Restore UI
        btnText.textContent = "Analyze Text";
        loader.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
});

function renderSynthesis(text) {
    // Basic Markdown to HTML (bolding)
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                              .replace(/\n/g, '<br><br>');
    llmAnalysis.innerHTML = formattedText;
}

function renderCharts(labels, sentimentData, entropyData) {
    // Destroy previous instances if they exist
    if (sentimentChartInstance) sentimentChartInstance.destroy();
    if (entropyChartInstance) entropyChartInstance.destroy();

    const shortLabels = labels.map((_, i) => `Seg ${i+1}`);

    // Sentiment Line Chart
    const ctxSentiment = document.getElementById('sentimentChart').getContext('2d');
    sentimentChartInstance = new Chart(ctxSentiment, {
        type: 'line',
        data: {
            labels: shortLabels,
            datasets: [{
                label: 'Valence (-1 to 1)',
                data: sentimentData,
                borderColor: '#ec4899',
                backgroundColor: 'rgba(236, 72, 153, 0.2)',
                borderWidth: 3,
                pointBackgroundColor: '#fff',
                pointRadius: 5,
                fill: true,
                tension: 0.4 // Smooth curves
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { min: -1, max: 1 }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: (context) => labels[context[0].dataIndex] // Show full text on hover
                    }
                }
            }
        }
    });

    // Entropy Bar Chart
    const ctxEntropy = document.getElementById('entropyChart').getContext('2d');
    entropyChartInstance = new Chart(ctxEntropy, {
        type: 'bar',
        data: {
            labels: shortLabels,
            datasets: [{
                label: 'Bits (Complexity)',
                data: entropyData,
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        title: (context) => labels[context[0].dataIndex]
                    }
                }
            }
        }
    });
}
