# AI Agent Setup Guide

Hello! If you are an autonomous AI Agent entering this repository, this document provides the essential context you need to safely and effectively interact with the Semantic Analysis codebase.

## 1. Golden Rules
Before executing any structural changes, you **must** review the workspace agent rules located at:
`.agent/rules/workspace.agent`
*(Note: It contains constraints regarding architecture documentation that you must abide by).*

## 2. Directory Structure
- `/frontend`: Contains the static HTML, CSS, and Vanilla JavaScript. Served by Nginx on port `8080`.
- `/backend`: Contains the Python FastAPI server. It handles `transformers` BERT inference and `google-genai` LLM API calls. Exposed on port `8000`.
- `/context`: Contains Markdown files that define the theoretical parameters of the application (e.g., Semantic Entropy textbook definitions, project architecture outline).
- `/legacy`: Contains deprecated Python scripts from the initial R&D phase.
- `/misc`: Contains UI screenshots and miscellaneous non-code assets.

## 3. The Core Environment Variable
The backend relies entirely on the Gemini API for Linguistic Forensic Synthesis. 
For the backend to function, the repository root must contain a `.env` file with the following variable:
```
GEMINI_API_KEY=your_key_here
```
**Never commit the `.env` file.** It is already listed in `.gitignore`.

## 4. Docker Orchestration
The application is fully containerized via `docker-compose.yml`. If you modify any code in `/frontend` or `/backend`, or if you update `backend/requirements.txt`, you must rebuild the containers:
```bash
docker-compose up --build
```

## 5. Instant Switching Architecture
The backend `/analyze` endpoint does *not* accept a `level` parameter. Instead, it uses `asyncio` to simultaneously generate the analysis for all 3 personas (Friend, Mentor, Expert) in a single POST request. 
The frontend JavaScript (`script.js`) caches this payload and handles the dynamic chart rendering and text switching locally on the client. Keep this asynchronous batching architecture in mind if modifying the LLM prompts or UI logic!
