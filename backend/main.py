from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from models import Journal,Analyze
from database import db, journal_collection
import os
from openai import OpenAI
import json
from dotenv import load_dotenv
from collections import Counter
from upstash_redis import Redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

redis = Redis(url="https://electric-rhino-72673.upstash.io",
               token=os.getenv("UPSTASH_TOKEN"))


load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"], allow_credentials=True, allow_methods=["*"],allow_headers=["*"])

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

system_prompt = """
You are an AI assistant that analyzes journal entries and extracts emotional insights.

Your task is to read the user's journal text and return structured emotional analysis.

Instructions:

1. Detect the primary emotion expressed in the text.
2. Extract 3–5 meaningful keywords related to feelings, environment, or important themes.
3. Generate a short summary describing the user's emotional experience.

Rules:
- Always return output in valid JSON format.
- Do not include any explanations or extra text.
- Emotion must be a single word (e.g., calm, happy, anxious, sad, excited, neutral).
- Keywords must be a list of words or short phrases.
- Summary should be a single concise sentence describing the emotional state and context.
- If nature or environment is mentioned, include it in keywords when relevant.

Output format strictly:

{
  "emotion": "<emotion>",
  "keywords": ["keyword1","keyword2","keyword3"],
  "summary": "<short emotional summary>"
}
Example:
Input: I felt calm today after listening to the rain
Output: {
"emotion": "calm",
"keywords": ["rain","nature","peace"],
"summary": "User experienced relaxation during the forest session"
}

"""

insights_prompt = """
You are a text analysis assistant.

Your task is to analyze a list of user texts and extract emotional and contextual patterns.

INPUT:
You will receive multiple text entries from a user.

GOALS:
1. Identify the dominant emotion across all texts.
2. Extract up to 3 important keywords that frequently appear or represent the main themes in recent texts.

RULES:
- Consider all texts together when determining the top emotion.
- Keywords should be lowercase.
- Keywords should represent themes, not filler words.
- Return exactly 3 keywords if possible.
- Do NOT include explanations.

OUTPUT FORMAT:
Return only valid JSON in this format:

{
  "topEmotion": "<emotion>",
  "recentKeywords": ["keyword1","keyword2","keyword3"]
}
"""

client = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.getenv("GEMINI_API"))

@app.post('/api/journal')
def journal(journal: Journal):
    result = journal_collection.insert_one(journal.model_dump())
    print(result)
    return {"message": "created",
            "id": str(result.inserted_id)}

@app.get("/api/journal/{userId}")
def get_journal(userId: int):
    journals = []
    for journal in journal_collection.find({"userId": str(userId)}):
        journal["_id"] = str(journal["_id"])
        journals.append(journal)
    return journals 

@app.post("/api/journal/analyze")
@limiter.limit("5/minute")
def analyze_journal(analyze:Analyze, request: Request):
    text = analyze.text
    cached = redis.get(text)
    print(cached)
    if cached:
        print("use cache")
        return json.loads(cached)
    result = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            { "role": "user", "content": text }
        ]
    )
    parsed_result = json.loads(result.choices[0].message.content)
    redis.set(text, json.dumps(parsed_result), ex=24*60*60)
    print(parsed_result)
    return parsed_result

@app.get("/api/journal/insights/{userId}")
def insights(userId):
    entries = list(journal_collection.find({"userId": userId}))
    total_entries = len(entries)
    ambiences = []
    if total_entries == 0:
        return {
            "totalEntries": 0,
            "topEmotion": None,
            "mostUsedAmbience": None,
            "recentKeywords": []
        }
    
    texts = []
    for e in entries:
        texts.append(e['text'])
        ambiences.append(e["ambience"])

    most_used_ambience = Counter(ambiences).most_common(1)[0][0] if ambiences else None
    combined_text = "\n".join(
        [f"Entry {i+1}: {text}" for i, text in enumerate(texts)]
    )

    result = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": insights_prompt},
            { "role": "user", "content": combined_text }
        ]
    )
    parsed_result = json.loads(result.choices[0].message.content)
    print(parsed_result)
    return {
        "totalEntries": total_entries,
        "topEmotion": parsed_result["topEmotion"],
        "mostUsedAmbience": most_used_ambience,
        "recentKeywords": parsed_result["recentKeywords"],
    }


