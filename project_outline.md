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
   - **LLM Integration:** Formats the calculated metrics and original text into a prompt and calls the Gemini API to return a dynamic, human-readable forensic linguistic synthesis.

3. **Deployment Foundation**
   - **Tech:** Docker, Docker Compose, Nginx.
   - **Role:** Containerizes the application for consistent deployment on cloud Virtual Private Servers (VPS). Nginx acts as a reverse proxy to handle traffic and SSL termination.

## Flow of Data
1. User enters text in the web UI.
2. Frontend sends an HTTP POST request to `/analyze` on the Backend.
3. Backend NLP models score sentiment and calculate entropy.
4. Backend prompts Gemini LLM with the scores and text.
5. Backend returns a JSON response: `{ segments: [...], sentiment: [...], entropy: [...], analysis: "..." }`
6. Frontend parses the JSON and renders interactive charts and the summary text.
