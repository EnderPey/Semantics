import os
import re
import math
from collections import Counter
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup FastAPI
app = FastAPI(title="Sentiment Analysis API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load BERT Model
print("Loading BERT model...")
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using gemini-1.5-flash or gemini-pro (for free tier access)
model = genai.GenerativeModel('gemini-1.5-flash')

class AnalyzeRequest(BaseModel):
    text: str

def calculate_entropy(segment: str) -> float:
    tokens = re.findall(r'\b\w+\b', segment.lower())
    if not tokens: return 0.0
    counts = Counter(tokens)
    probs = [count/len(tokens) for count in counts.values()]
    return -sum(p * math.log2(p) for p in probs)

@app.post("/analyze")
async def analyze_text(req: AnalyzeRequest):
    text = req.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # Segment the text
    segments = [s.strip() for s in re.split(r'[.,]', text) if s.strip()]
    if not segments:
        raise HTTPException(status_code=400, detail="Could not extract segments.")

    bert_scores = []
    entropy_scores = []

    for seg in segments:
        # Sentiment
        result = sentiment_analyzer(seg)[0]
        star_rating = int(result['label'].split()[0])
        normalized_score = (star_rating - 3) / 2
        bert_scores.append(normalized_score)

        # Entropy
        entropy = calculate_entropy(seg)
        entropy_scores.append(entropy)

    # Prepare prompt for LLM
    stats_summary = "\\n".join([
        f"Segment {i+1}: '{s}' -> Sentiment: {bert_scores[i]:.2f}, Entropy: {entropy_scores[i]:.2f} bits"
        for i, s in enumerate(segments)
    ])
    
    prompt = f"""
You are a professor of Semantic Analysis providing a "Linguistic Forensic Synthesis".
Analyze the following text divided into segments. For each segment, you are provided a sentiment score (-1.0 to 1.0, where -1 is negative and 1 is positive) and a Shannon entropy score (which measures unpredictability/complexity; higher means more unique lexical choices).

Text Segments and Scores:
{stats_summary}

Based on these metrics, provide a concise, insightful 1-2 paragraph analysis explaining the emotional trajectory (e.g., U-shaped narrative, negative face redress) and cognitive effort (high entropy vs low entropy clichés) of the sender. Frame it as a forensic linguistic evaluation. Make it sound professional and slightly academic, but highly engaging.
"""

    try:
        response = model.generate_content(prompt)
        analysis_text = response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        analysis_text = "LLM analysis temporarily unavailable. Please check API key configuration."

    return {
        "segments": segments,
        "sentiment": bert_scores,
        "entropy": entropy_scores,
        "analysis": analysis_text
    }
