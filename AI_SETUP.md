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

## 6. Mock Mode (Critical for Agents)
If you do not have access to a valid `GEMINI_API_KEY`, set the following environment variable before running the app or tests:
```
USE_MOCK_LLM=true
```
This bypasses all Gemini API calls and returns realistic pre-written mock analyses for all 3 personas. The BERT sentiment scoring and entropy calculations still run normally. Use this mode for all development and testing to avoid burning API credits.

## 7. Automated Testing
Before committing any backend changes, you **must** run the test suite:
```bash
cd backend && USE_MOCK_LLM=true pytest tests/ -v
```
The tests validate the `/analyze` endpoint's JSON structure, error handling, and score ranges. All tests run in Mock Mode so no API key is required.

## 8. Error Logging
If the FastAPI server crashes or behaves unexpectedly, read the log file at:
```
backend/logs/error.log
```
This file contains timestamped tracebacks from all backend errors. Read this **before** attempting any debugging.

## 9. Context Navigation
Before modifying code, read `context/INDEX.md` first. It maps each documentation file to the type of task it is relevant for, so you can selectively load only the context you need.
