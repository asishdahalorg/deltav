import streamlit as st
import yfinance as yf
import pandas as pd

version = "0.0.1"
# --- CONFIGURATION ---
st.set_page_config(
    page_title="Delta V | Volatility Analyzer",
    layout="wide"
)

# --- HEADER ---
st.title("Delta V | Market Volatility Analyzer")
st.markdown(f"### v{version}")
st.markdown("---")

# --- INPUTS ---
with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Ticker Symbol", value="AMPX").upper()
    period = st.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y"], index=0)

# --- EXECUTION ---
if ticker:
    st.write(f"Acquiring data for: **{ticker}**")
    
    try:
        # Fetch data with progress bar disabled for cleaner UI
        df = yf.download(ticker, period=period, progress=False)
        
        if not df.empty:
            # Data Processing
            # Explicitly cast to float to prevent serialization errors
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            price_change = current_price - prev_price
            
            # Key Metrics Display
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric(
                    label="Current Price (USD)", 
                    value=f"${current_price:.2f}", 
                    delta=f"{price_change:.2f}"
                )
            
            # Visualization
            st.subheader("Price History")
            st.line_chart(df['Close'])
            
            # Data Inspection
            with st.expander("View Raw Data"):
                st.dataframe(df.tail())
                
        else:
            st.warning(f"No data found for ticker '{ticker}'. Please verify the symbol.")
            
    except Exception as e:
        st.error(f"System Error: {e}")