import requests
from newspaper import Article
from transformers import pipeline
from rake_nltk import Rake
from gtts import gTTS
import os

# Initialize models
sentiment_pipeline = pipeline('sentiment-analysis')
summarizer = pipeline('summarization')
rake = Rake()

def fetch_news(company):
    api_key = os.getenv("NEWS_API_KEY")
    response = requests.get(
        f"https://newsapi.org/v2/everything?q={company}&apiKey={api_key}&pageSize=10"
    )
    return [article["url"] for article in response.json().get("articles", [])]

def process_articles(urls):
    processed = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            summary = summarizer(article.text[:1024], max_length=150)[0]['summary_text']
            sentiment = sentiment_pipeline(summary[:512])[0]['label']
            rake.extract_keywords_from_text(article.text)
            topics = rake.get_ranked_phrases()[:3]
            processed.append({
                "title": article.title,
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics
            })
        except Exception as e:
            continue
    return processed

def generate_comparative_analysis(articles):
    # Implement comparative logic
    return {"final_sentiment": "Overall positive sentiment"}

def generate_hindi_tts(text):
    tts = gTTS(text=text, lang='hi')
    tts.save("output.mp3")
    return "output.mp3"