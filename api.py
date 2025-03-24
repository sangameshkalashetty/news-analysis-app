from fastapi import FastAPI
from pydantic import BaseModel
from utils import fetch_news, process_articles, generate_comparative_analysis, generate_hindi_tts
import os

app = FastAPI()

class CompanyRequest(BaseModel):
    company: str

@app.post("/analyze")
async def analyze_news(request: CompanyRequest):
    articles = fetch_news(request.company)
    processed_articles = process_articles(articles)
    comparative = generate_comparative_analysis(processed_articles)
    audio_path = generate_hindi_tts(comparative["final_sentiment"])
    
    return {
        "company": request.company,
        "articles": processed_articles,
        "comparative_sentiment": comparative,
        "audio_url": f"http://{os.getenv('HOST')}/audio/{audio_path}"
    }