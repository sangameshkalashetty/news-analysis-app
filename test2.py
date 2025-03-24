# app.py
import streamlit as st
import requests
import os
import json
from newspaper import Article
from textblob import TextBlob
from rake_nltk import Rake
from gtts import gTTS
from collections import defaultdict
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Utility functions
def get_clean_domain(url):
    """Extract clean domain name from URL"""
    return urlparse(url).netloc.replace('www.', '').split('.')[0]

def analyze_sentiment(text):
    """Perform sentiment analysis using TextBlob"""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Positive"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative"
    return "Neutral"

def generate_comparative_analysis(articles):
    """Generate comparative analysis report"""
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

def main():
    st.title("News Analysis Dashboard")
    company = st.text_input("Enter Company Name", "Tesla")
    
    if st.button("Analyze"):
        # 1. Fetch News Articles
        news_api_key = os.getenv("NEWS_API_KEY")
        response = requests.get(
            f"https://newsapi.org/v2/everything?q={company}&apiKey={news_api_key}&pageSize=10"
        )
        
        if response.status_code != 200:
            st.error("Failed to fetch news articles")
            return
            
        raw_articles = response.json().get('articles', [])[:10]  # Get first 10 articles
        
        # 2. Process Articles
        processed_articles = []
        for article in raw_articles:
            try:
                news_item = Article(article['url'])
                news_item.download()
                news_item.parse()
                
                # Generate summary (first 200 characters as fallback)
                summary = news_item.text[:200] + "..." if news_item.text else ""
                
                # Extract topics
                rake = Rake()
                rake.extract_keywords_from_text(news_item.text)
                topics = rake.get_ranked_phrases()[:3]
                
                processed_articles.append({
                    "title": news_item.title,
                    "summary": summary,
                    "sentiment": analyze_sentiment(news_item.text),
                    "topics": topics,
                    "source": get_clean_domain(article['url'])
                })
            except Exception as e:
                st.write(f"Error processing {article['url']}: {str(e)}")
                continue
        
        # 3. Generate Comparative Analysis
        comparison = generate_comparative_analysis(processed_articles)
        
        # 4. Generate Structured Report
        final_report = {
            "company": company,
            "articles": processed_articles,
            "comparative_sentiment_score": comparison,
            "final_sentiment_analysis": (
                f"{company}'s news coverage shows "
                f"{max(comparison['sentiment_distribution'], key=comparison['sentiment_distribution'].get)} "
                "sentiment overall"
            )
        }
        
        # 5. Generate Hindi TTS
        tts_text = (
            f"{company} के बारे में {len(processed_articles)} समाचार लेख मिले। "
            f"समग्र भावना {comparison['sentiment_distribution']} है। "
            "मुख्य विषय हैं: " + ", ".join(comparison['topic_overlap']['common_topics'])
        )
        tts = gTTS(text=tts_text, lang='hi')
        tts.save("output.mp3")
        
        # Display Results
        st.subheader("Structured Report")
        st.json(final_report)
        
        st.subheader("Comparative Analysis")
        st.write("### Sentiment Distribution")
        st.bar_chart(comparison['sentiment_distribution'])
        
        st.write("### Topic Overview")
        st.write("Common Topics:", ", ".join(comparison['topic_overlap']['common_topics']))
        st.write("Unique Topics:", ", ".join(comparison['topic_overlap']['unique_topics']))
        
        st.subheader("Hindi Summary Audio")
        st.audio("output.mp3")

if __name__ == "__main__":
    main()