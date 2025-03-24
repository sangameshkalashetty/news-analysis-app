# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from gtts import gTTS
import json
from collections import defaultdict
import os
from urllib.parse import urlparse

# Utility functions
def get_clean_domain(url):
    return urlparse(url).netloc.replace('www.', '').split('.')[0]

def extract_articles(query):
    """Mock news extraction - replace with actual scraping"""
    return [
        {
            "url": "https://example.com/tesla-sales-record",
            "content": "Tesla's Q3 sales exceeded expectations with 500,000 vehicles delivered globally...",
            "title": "Tesla's New Model Breaks Sales Records"
        },
        {
            "url": "https://example.com/tesla-regulation",
            "content": "New regulations in Europe target Tesla's autonomous driving features...",
            "title": "Regulatory Scrutiny on Tesla's Self-Driving Tech"
        }
    ]

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1: return "Positive"
    if analysis.sentiment.polarity < -0.1: return "Negative"
    return "Neutral"

def generate_comparative_analysis(articles):
    sentiment_counts = defaultdict(int)
    all_topics = defaultdict(int)
    
    for article in articles:
        sentiment_counts[article['sentiment']] += 1
        for topic in article['topics']:
            all_topics[topic] += 1
            
    common_threshold = len(articles) // 2
    common_topics = [k for k,v in all_topics.items() if v >= common_threshold]
    unique_topics = [k for k,v in all_topics.items() if v == 1]
    
    return {
        "sentiment_distribution": dict(sentiment_counts),
        "topic_overlap": {
            "common_topics": common_topics,
            "unique_topics": unique_topics
        }
    }

# Streamlit UI
st.title("News Analysis Dashboard")
company = st.text_input("Enter Company Name", "Tesla")

if st.button("Analyze"):
    # News Extraction
    articles = extract_articles(company)
    
    processed = []
    for article in articles:
        # Sentiment Analysis
        sentiment = analyze_sentiment(article['content'])
        
        # Topic Extraction (simplified)
        topics = ["Electric Vehicles", "Innovation"] if "sales" in article['title'] else ["Regulations"]
        
        processed.append({
            "title": article['title'],
            "summary": article['content'][:100] + "...",
            "sentiment": sentiment,
            "topics": topics
        })
    
    # Comparative Analysis
    comparison = generate_comparative_analysis(processed)
    
    # Generate TTS
    tts_text = f"{company} के बारे में {len(processed)} समाचार लेख मिले। समग्र भावना {comparison['sentiment_distribution']} है।"
    tts = gTTS(text=tts_text, lang='hi')
    tts.save("output.mp3")
    
    # Display Results
    report = {
        "company": company,
        "articles": processed,
        "comparative_sentiment_score": comparison,
        "final_sentiment_analysis": f"{company}'s news coverage shows {max(comparison['sentiment_distribution'], key=comparison['sentiment_distribution'].get)} sentiment",
        "audio": "output.mp3"
    }
    
    st.json(report)
    st.audio("output.mp3")

st.markdown("""
# News Analysis Summary
This application provides a summary of the news article using AI-powered analysis.
You can upload a news article or paste the content directly.
""") 