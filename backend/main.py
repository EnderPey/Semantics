import os
import re
import math
import asyncio
from collections import Counter
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from google import genai
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
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    
    instructions = {
        "friend": "Act like a supportive, empathetic friend. Focus entirely on feelings. Keep it casual and warm. Use accessible language and avoid any complex terminology.",
        "mentor": "Act like a wise communication mentor. Provide constructive feedback on the flow and tone of the message. Point out areas of improvement and suggest how the message comes across.",
        "expert": "You are a professor of Semantic Analysis providing a 'Linguistic Forensic Synthesis'. Frame it as a forensic linguistic evaluation. Make it sound professional and slightly academic, but highly engaging."
    }

    async def fetch_analysis(level: str) -> str:
        prompt = f"""
{instructions[level]}

The following text is a standalone message from an arbitrary author. Do not assume the user providing this text is the author. Analyze the author of the text based on the segments below. For each segment, you are provided a sentiment score (-1.0 to 1.0, where -1 is negative and 1 is positive) and a Shannon entropy score (which measures unpredictability/complexity).

Text Segments and Scores:
{stats_summary}

Based on these metrics, provide a concise, insightful analysis explaining the emotional trajectory and cognitive effort of the sender. 
IMPORTANT: Limit your response to a maximum of 2 paragraphs.
"""
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error ({level}): {e}")
            return "LLM analysis temporarily unavailable."

    # Run all 3 concurrently
    results = await asyncio.gather(
        fetch_analysis("friend"),
        fetch_analysis("mentor"),
        fetch_analysis("expert")
    )

    return {
        "segments": segments,
        "sentiment": bert_scores,
        "entropy": entropy_scores,
        "analyses": {
            "friend": results[0],
            "mentor": results[1],
            "expert": results[2]
        }
    }
