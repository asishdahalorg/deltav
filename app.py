import streamlit as st
import yfinance as yf
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv() # Load variables from .env
st.set_page_config(page_title="Delta-V Analyzer", layout="wide")

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("Missing Google API Key. Please check your .env file.")

# --- HEADER ---
version = "0.0.3"
st.title("Delta V | Market Volatility Analyzer")
st.markdown(f"### v{version}")
st.markdown("---")

# --- INPUTS ---
with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    period = st.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y"], index=2) 

# --- HELPER FUNCTIONS ---
def get_ai_sentiment(ticker_symbol, headlines):
    """
    Sends headlines to Gemini for sentiment analysis.
    Returns: A tuple (Sentiment Score, Explanation)
    """
    if not api_key:
        return 0, "AI Offline"

    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    You are a cynical Wall Street trader. Analyze these headlines for {ticker_symbol}:
    {headlines}
    
    Return a single JSON object with two fields:
    1. "score": A float between -1.0 (Bearish) and 1.0 (Bullish).
    2. "reason": A 1-sentence explanation of why.
    """

    try:
        response = model.generate_content(prompt)
        # Simple string parsing since we want speed (in prod, use strict JSON parsing)
        # This is a 'hacky' parse to handle the text response
        text = response.text
        # Cleanup markdown if present
        text = text.replace("```json", "").replace("```", "").strip()
        import json
        data = json.loads(text)
        return data["score"], data["reason"]
    except Exception as e:
        return 0, f"Analysis Failed: {e}"

# --- EXECUTION ---
if ticker:
    st.write(f"Acquiring data for: **{ticker}**")

    try:
        # 1. Fetch Market Data
        df = yf.download(ticker, period=period, progress=False)

        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df = df.dropna()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()

            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            price_change = current_price - prev_price
            current_sma = df['SMA_20'].iloc[-1]

            # 2. THE AI BLOCK (New!)
            st.subheader("🤖 AI Sentiment Analysis")

            # SIMULATION: In a real app, we'd scrape news here.
            # For this prototype, we inject 'Sample' headlines to prove the connection works.
            sample_headlines = [
                f"{ticker} announces breakthrough in efficiency.",
                f"Analysts upgrade {ticker} price target significantly.",
                f"Market rallies as tech sector shows strength."
            ]

            with st.spinner(f"Consulting Gemini about {ticker}..."):
                # Call our function
                sentiment_score, sentiment_reason = get_ai_sentiment(ticker, sample_headlines)

            # Display AI Results
            ai_col1, ai_col2 = st.columns([1, 4])
            with ai_col1:
                # Color code the sentiment
                if sentiment_score > 0.2:
                    sent_color = "normal" # Streamlit metric green
                elif sentiment_score < -0.2:
                    sent_color = "inverse" # Streamlit metric red
                else:
                    sent_color = "off"

                st.metric(label="Gemini Sentiment Score", value=sentiment_score, delta=None)

            with ai_col2:
                st.info(f"**AI Analyst:** {sentiment_reason}")
                st.caption(f"Based on simulated headlines: {sample_headlines}")

            st.markdown("---")

            # 3. Technical Visuals (Existing)
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric(label="Current Price", value=f"${current_price:.2f}", delta=f"{price_change:.2f}")

            st.subheader("Price vs. Trend (20-Day SMA)")
            st.line_chart(df[['Close', 'SMA_20']])

        else:
            st.warning(f"No data found for {ticker}.")

    except Exception as e:
        st.error(f"System Error: {e}")