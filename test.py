# app.py (Modified version)
import streamlit as st
import requests
from textblob import TextBlob  # Alternative to transformers
from newspaper import Article
from rake_nltk import Rake
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Positive"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative"
    return "Neutral"

def main():
    st.title("News Analysis App")
    company = st.text_input("Enter Company Name")
    
    if st.button("Analyze"):
        # 1. Fetch News
        news_api_key = os.getenv("NEWS_API_KEY")
        response = requests.get(
            f"https://newsapi.org/v2/everything?q={company}&apiKey={news_api_key}&pageSize=5"
        )
        
        if response.status_code != 200:
            st.error("Failed to fetch news articles")
            return
            
        articles = response.json().get('articles', [])[:3]  # Limit to 3 articles
        
        # 2. Process Articles
        results = []
        for article in articles:
            try:
                a = Article(article['url'])
                a.download()
                a.parse()
                
                summary = a.text[:200] + "..."  # Simple summary
                sentiment = analyze_sentiment(a.text)
                
                rake = Rake()
                rake.extract_keywords_from_text(a.text)
                topics = rake.get_ranked_phrases()[:3]
                
                results.append({
                    "title": a.title,
                    "summary": summary,
                    "sentiment": sentiment,
                    "topics": topics
                })
            except Exception as e:
                st.write(f"Error processing {article['url']}: {str(e)}")
                continue
        
        # 3. Display Results
        for res in results:
            st.subheader(res['title'])
            st.write(f"**Sentiment**: {res['sentiment']}")
            st.write(f"**Summary**: {res['summary']}")
            st.write(f"**Topics**: {', '.join(res['topics'])}")
            st.markdown("---")
        
        # 4. Generate Hindi TTS
        if results:
            tts = gTTS(text=f"{company} के बारे में {len(results)} लेख मिले", lang='hi')
            tts.save("output.mp3")
            st.audio("output.mp3")

if __name__ == "__main__":
    main()