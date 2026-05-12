# Sentiment Analysis Website Project Outline

## Goal
To build a web application that takes user text/messages as input, performs deep linguistic analysis, and provides visual and textual insights. The analysis calculates emotional sentiment and semantic entropy, generating a unique summary per input using a Large Language Model.

## Architecture

1. **Frontend (User Interface)**
   - **Tech:** Vanilla HTML, CSS, JavaScript.
   - **Role:** Provides a premium, interactive interface for users to input text. Displays dynamic charts (Chart.js) of sentiment and entropy and a synthesized text summary.

2. **Backend (API Engine)**
   - **Tech:** Python, FastAPI.
   - **Role:** Receives text, segments it by clauses/sentences, and runs the analytical models. 
   - **NLP Pipeline:** Uses `transformers` (`nlptown/bert-base-multilingual-uncased-sentiment`) to score the sentiment of each segment. Calculates Shannon Entropy for the lexical unpredictability of each segment.
   - **LLM Integration:** Asynchronously batches 3 concurrent calls to the Gemini 2.5 Flash API to generate Friend, Mentor, and Expert personas simultaneously. The entire package is returned to the frontend for instant switching.

3. **Deployment Foundation**
   - **Tech:** Docker, Docker Compose, Nginx.
   - **Role:** Containerizes the application for consistent deployment on cloud Virtual Private Servers (VPS). Nginx acts as a reverse proxy to handle traffic and SSL termination.

## Flow of Data
1. User enters text in the web UI.
2. Frontend sends an HTTP POST request to `/analyze` on the Backend.
3. Backend NLP models score sentiment and calculate entropy.
4. Backend concurrently prompts Gemini LLM for 3 different personas.
5. Backend returns a JSON response containing arrays for segments, sentiment, and entropy, plus a dictionary of the 3 analyses.
6. Frontend parses the JSON, caches it globally, and instantly renders interactive charts and summary text based on the dropdown selection.
