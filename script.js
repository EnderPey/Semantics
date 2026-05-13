const analyzeBtn = document.getElementById('analyzeBtn');
const textInput = document.getElementById('textInput');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');
const resultsSection = document.getElementById('resultsSection');

// ==== Demo Mock Mode ==== //
// When TRUE the UI will skip the backend call and use pre‑written analyses.
// This is the default for the static GitHub Pages demo.
const USE_MOCK_UI = true;
const MOCK_ANALYSES = {
  friend: "Hey, it looks like the author was going through a mix of emotions here. Some parts feel really warm and positive, while others carry a heavier, more uncertain tone. Overall though, the vibe is genuine and heartfelt.\n\nIt seems like they put real thought into what they were saying — the word choices aren't random, they're intentional. That kind of effort shows they really care about getting their message across.",
  mentor: "The emotional arc of this message reveals a thoughtful communicator who transitions between vulnerability and assertiveness. The sentiment trajectory suggests the author began cautiously before building confidence in their core message.\n\nFrom a structural standpoint, the entropy scores indicate deliberate lexical choices rather than stream‑of‑consciousness writing. This is a sign of someone who edits mentally before committing words — a strong communication habit worth reinforcing.",
  expert: "Linguistic Forensic Synthesis: The semantic trajectory of this text exhibits a measurable oscillation between affective valence states, with the author's sentiment arc progressing from a neutral‑to‑negative baseline toward a distinctly positive terminal segment. The Shannon entropy values remain moderate throughout, suggesting controlled lexical diversity rather than impulsive verbalization.\n\nThe cognitive load distribution, as evidenced by entropy variance across segments, indicates a pre‑meditated compositional strategy. The author demonstrates metacognitive awareness of their audience, calibrating emotional intensity against informational density in a manner consistent with high‑stakes interpersonal communication."
};
const llmAnalysis = document.getElementById('llmAnalysis');

let sentimentChartInstance = null;
let entropyChartInstance = null;
let vibeChartInstance = null;
let globalAnalysisData = null;

const analysisLevel = document.getElementById('analysisLevel');
analysisLevel.addEventListener('change', (e) => {
    if (!globalAnalysisData) return;
    const level = e.target.value;
    renderSynthesis(globalAnalysisData.analyses[level]);
    renderCharts(globalAnalysisData.segments, globalAnalysisData.sentiment, globalAnalysisData.entropy, level);
});

// Chart.js default theme configuration for light mode
Chart.defaults.color = '#6b7280';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';

analyzeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) return alert("Please enter some text to analyze.");

    // UI Loading state
    btnText.textContent = "Analyzing...";
    loader.classList.remove('hidden');
    analyzeBtn.disabled = true;
    resultsSection.classList.add('hidden');

    try {
        let data;

        if (USE_MOCK_UI) {
            // --- Static demo mode: generate mock data locally ---
            const segments = text.split(/[.,!?]/).map(s => s.trim()).filter(s => s.length > 0);
            const sentiment = segments.map(() => +(Math.random() * 2 - 1).toFixed(2));
            const entropy   = segments.map(() => +(Math.random() * 4 + 0.5).toFixed(2));
            data = { segments, sentiment, entropy, analyses: MOCK_ANALYSES };
        } else {
            // --- Live backend mode ---
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            data = await response.json();
        }

        globalAnalysisData = data;

        const currentLevel = analysisLevel.value;
        renderSynthesis(data.analyses[currentLevel]);
        renderCharts(data.segments, data.sentiment, data.entropy, currentLevel);

        resultsSection.classList.remove('hidden');

    } catch (error) {
        console.error(error);
        alert("An error occurred during analysis. Make sure the backend is running.");
    } finally {
        btnText.textContent = "Analyze Text";
        loader.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
});

function renderSynthesis(text) {
    // Basic Markdown to HTML (bolding)
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Split by newlines and wrap in <p> tags
    const paragraphs = formattedText.split(/\n+/)
                                    .filter(p => p.trim() !== '')
                                    .map(p => `<p>${p}</p>`)
                                    .join('');
                                    
    llmAnalysis.innerHTML = paragraphs;
}

function renderCharts(labels, sentimentData, entropyData, level) {
    // Destroy previous instances if they exist
    if (sentimentChartInstance) sentimentChartInstance.destroy();
    if (entropyChartInstance) entropyChartInstance.destroy();
    if (vibeChartInstance) vibeChartInstance.destroy();

    const shortLabels = labels.map((_, i) => `Seg ${i+1}`);

    // UI Element References
    const vibeContainer = document.getElementById('vibeContainer');
    const sentimentContainer = document.getElementById('sentimentContainer');
    const entropyContainer = document.getElementById('entropyContainer');
    const tableContainer = document.getElementById('tableContainer');
    const chartsGrid = document.getElementById('chartsGrid');

    // Visibility Logic
    if (level === 'friend') {
        chartsGrid.style.display = 'block'; 
        vibeContainer.style.display = 'block';
        sentimentContainer.style.display = 'none';
        entropyContainer.style.display = 'none';
        tableContainer.style.display = 'none';

        // Calculate Overall Vibe
        let posCount = 0;
        let negCount = 0;
        sentimentData.forEach(val => {
            if (val > 0) posCount++;
            else negCount++;
        });
        const ctxVibe = document.getElementById('vibeChart').getContext('2d');
        vibeChartInstance = new Chart(ctxVibe, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative/Neutral'],
                datasets: [{
                    data: [posCount, negCount === 0 && posCount === 0 ? 1 : negCount],
                    backgroundColor: ['#10b981', '#f43f5e']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
        return; // Skip rendering other charts
    } 
    
    // For Mentor and Expert
    chartsGrid.style.display = 'grid';
    vibeContainer.style.display = 'none';
    sentimentContainer.style.display = 'block';

    if (level === 'expert') {
        entropyContainer.style.display = 'block';
        tableContainer.style.display = 'block';
        
        // Populate data table
        const tableBody = document.getElementById('segmentTableBody');
        tableBody.innerHTML = '';
        labels.forEach((text, i) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td class="seg-id">Seg ${i+1}</td><td class="seg-text">${text}</td>`;
            tableBody.appendChild(row);
        });
    } else {
        entropyContainer.style.display = 'none';
        tableContainer.style.display = 'none';
    }

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
