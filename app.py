import streamlit as st
import yfinance as yf
import pandas as pd

version = "0.0.2"

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
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    period = st.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y"], index=2) 

# --- EXECUTION ---
if ticker:
    st.write(f"Acquiring data for: **{ticker}**")
    
    try:
        # Fetch data
        df = yf.download(ticker, period=period, progress=False)
        
        if not df.empty:
            # --- CRITICAL FIX: FLATTEN COLUMNS ---
            # If yfinance returns a MultiIndex (e.g., ('Close', 'NVDA')), flatten it to just 'Close'
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # --- ANALYTIC LOGIC ---
            # 1. Clean Data
            df = df.dropna()
            
            # 2. Calculate Indicators
            # 20-Day Simple Moving Average
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            # 3. Key Data Points
            current_price = float(df['Close'].iloc[-1])
            prev_price = float(df['Close'].iloc[-2])
            price_change = current_price - prev_price
            
            # Get the latest SMA value
            current_sma = df['SMA_20'].iloc[-1]
            
            # --- DASHBOARD VISUALS ---
            
            # A. Metric Cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Current Price", 
                    value=f"${current_price:.2f}", 
                    delta=f"{price_change:.2f}"
                )
            
            with col2:
                # Dynamic Trend Indicator
                if pd.notna(current_sma):
                    if current_price > current_sma:
                        trend_color = ":green[BULLISH]" 
                        trend_desc = "Price > 20-Day SMA"
                    else:
                        trend_color = ":red[BEARISH]"
                        trend_desc = "Price < 20-Day SMA"
                        
                    st.markdown(f"**Trend Signal:** {trend_color}")
                    st.caption(f"Reason: {trend_desc}")
                else:
                    st.warning("Not enough data for Signal")

            # B. Main Chart
            st.subheader("Price vs. Trend (20-Day SMA)")
            
            # Now that columns are flat, this selection works perfectly
            st.line_chart(df[['Close', 'SMA_20']])
            
            # C. Raw Data Inspection
            with st.expander("View Analysis Data"):
                st.dataframe(df.tail(10))
                
        else:
            st.warning(f"No data found for ticker '{ticker}'. Please verify the symbol.")
            
    except Exception as e:
        st.error(f"System Error: {e}")