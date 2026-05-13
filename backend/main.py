import os
import re
import math
import asyncio
import logging
from collections import Counter
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----- Logging Configuration -----
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/error.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ----- Mock Mode -----
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
if USE_MOCK_LLM:
    logger.info("🧪 MOCK MODE ENABLED — Gemini API calls will be bypassed.")

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
logger.info("Loading BERT model...")
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
logger.info("BERT model loaded successfully.")

# Setup Gemini (skip if in mock mode)
if not USE_MOCK_LLM:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    logger.info("Gemini client initialized.")
else:
    client = None

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

    # ----- Mock LLM Responses -----
    mock_responses = {
        "friend": "Hey, it looks like the author was going through a mix of emotions here. Some parts feel really warm and positive, while others carry a heavier, more uncertain tone. Overall though, the vibe is genuine and heartfelt.\n\nIt seems like they put real thought into what they were saying — the word choices aren't random, they're intentional. That kind of effort shows they really care about getting their message across.",
        "mentor": "The emotional arc of this message reveals a thoughtful communicator who transitions between vulnerability and assertiveness. The sentiment trajectory suggests the author began cautiously before building confidence in their core message.\n\nFrom a structural standpoint, the entropy scores indicate deliberate lexical choices rather than stream-of-consciousness writing. This is a sign of someone who edits mentally before committing words — a strong communication habit worth reinforcing.",
        "expert": "Linguistic Forensic Synthesis: The semantic trajectory of this text exhibits a measurable oscillation between affective valence states, with the author's sentiment arc progressing from a neutral-to-negative baseline toward a distinctly positive terminal segment. The Shannon entropy values remain moderate throughout, suggesting controlled lexical diversity rather than impulsive verbalization.\n\nThe cognitive load distribution, as evidenced by entropy variance across segments, indicates a pre-meditated compositional strategy. The author demonstrates metacognitive awareness of their audience, calibrating emotional intensity against informational density in a manner consistent with high-stakes interpersonal communication."
    }

    async def fetch_analysis(level: str) -> str:
        if USE_MOCK_LLM:
            logger.info(f"Mock response generated for persona: {level}")
            return mock_responses[level]

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
            logger.error(f"Gemini API Error ({level}): {e}", exc_info=True)
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
