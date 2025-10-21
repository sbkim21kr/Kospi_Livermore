import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="KOSPI Livermore Screener", layout="centered")
st.title("🇰🇷 KOSPI Livermore Flow Finder")

# --- Livermore Metric Explanation ---
st.markdown("""
### 📘 What is Volume Spike?
**Volume Spike** measures how much today's trading volume exceeds the average volume over the past 20 days.  
It’s calculated as:  
**Volume Spike = Today's Volume ÷ 20-day Average Volume**  
A value above 2.0 suggests unusual trading activity — often a sign of accumulation or breakout behavior.

### 📈 What Do the Trend Words Mean?
The **Trend Direction** column shows the 20-day price trend:
- `upward`: Price is rising
- `downward`: Price is falling
- `sideways`: Price is stable
""")

# --- Load Main Data ---
try:
    df = pd.read_csv('latest_kospi.csv')
except FileNotFoundError:
    st.error("No data file found. Please run refresh.py or wait for GitHub Actions to update.")
    st.stop()

# --- Show Timestamp ---
timestamp = datetime.fromtimestamp(os.path.getmtime('latest_kospi.csv')).strftime('%Y-%m-%d %H:%M:%S')
st.markdown(f"**📅 Data retrieved at:** `{timestamp} KST`")

# --- Filter Input ---
st.markdown("### 🔍 Filter by Volume Spike")
min_volume_spike = st.number_input("Minimum Volume Spike", min_value=1.0, max_value=10.0, value=2.0, step=0.1)

# --- Apply Filter ---
filtered = df[df['Volume Spike'] >= min_volume_spike].copy()

# --- Ensure numeric columns safely ---
for col in ['MarketCap', 'Volume', 'Close', 'Volume Spike', '20-day Avg Close']:
    if col in filtered.columns:
        filtered[col] = pd.to_numeric(filtered[col], errors='coerce')

# --- Add raw columns for sorting ---
for col in ['MarketCap', 'Volume', 'Close', 'Volume Spike']:
    raw_col = f"{col}_raw"
    if col in filtered.columns:
        filtered[raw_col] = filtered[col]

# --- Add Trend Direction column ---
def get_trend(row):
    try:
        change = (row['Close_raw'] - row['20-day Avg Close']) / row['20-day Avg Close']
        return "upward" if change > 0.03 else "downward" if change < -0.03 else "sideways"
    except:
        return ""

filtered['Trend Direction'] = filtered.apply(get_trend, axis=1)

# --- Display Breakout Stocks ---
st.markdown("### 📋 Breakout Stocks")
display_df = filtered.copy()
display_df['MarketCap'] = display_df['MarketCap_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
display_df['Volume'] = display_df['Volume_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
display_df['Close'] = display_df['Close_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
display_df['Volume Spike'] = display_df['Volume Spike_raw'].round(2)

st.dataframe(
    display_df[['Code', 'Name', 'MarketCap_raw', 'Close_raw', 'Trend Direction', 'Volume_raw', 'Volume Spike_raw']]
    .rename(columns={
        'MarketCap_raw': 'MarketCap',
        'Close_raw': 'Close',
        'Volume_raw': 'Volume',
        'Volume Spike_raw': 'Volume Spike'
    }),
    use_container_width=True
)

