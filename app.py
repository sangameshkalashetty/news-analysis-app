import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("News Summarization & Sentiment Analysis")

company = st.text_input("Enter Company Name")
if st.button("Analyze"):
    response = requests.post(f"{BACKEND_URL}/analyze", json={"company": company})
    if response.status_code == 200:
        report = response.json()
        st.subheader(f"Report for {report['company']}")
        
        # Display articles
        for article in report["articles"]:
            st.write(f"**Title**: {article['title']}")
            st.write(f"**Summary**: {article['summary']}")
            st.write(f"**Sentiment**: {article['sentiment']}")
            st.write(f"**Topics**: {', '.join(article['topics'])}")
            st.markdown("---")
        
        # Comparative analysis
        st.subheader("Comparative Analysis")
        st.write(f"**Sentiment Distribution**: {report['comparative_sentiment']['sentiment_distribution']}")
        
        # Audio output
        st.audio(report["audio_url"], format="audio/mp3")
    else:
        st.error("Error processing request")