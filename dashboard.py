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

# --- Format numbers with commas ---
for col in ['MarketCap', 'Volume', 'Close']:
    if col in filtered.columns:
        filtered[col] = filtered[col].apply(lambda x: f"{int(x):,}")

# --- Display Table ---
st.markdown("### 📋 Breakout Stocks")
st.dataframe(filtered[['Code', 'Name', 'MarketCap', 'Close', 'Volume', 'Volume Spike']])

# --- Download as TXT ---
txt = filtered[['Code', 'Name', 'MarketCap', 'Close', 'Volume', 'Volume Spike']].to_string(index=False)
st.download_button(
    label="📥 Download Filtered Results as TXT",
    data=txt,
    file_name='filtered_kospi.txt',
    mime='text/plain'
)

# --- Historical Archive Viewer ---
st.markdown("### 📅 Historical Snapshots")
if os.path.exists('data'):
    archive_files = sorted(os.listdir('data'), reverse=True)
    selected_file = st.selectbox("Choose a date to view", archive_files)
    if selected_file:
        archive_df = pd.read_csv(f'data/{selected_file}')
        for col in ['MarketCap', 'Volume', 'Close']:
            if col in archive_df.columns:
                archive_df[col] = archive_df[col].apply(lambda x: f"{int(x):,}")
        st.dataframe(archive_df[['Code', 'Name', 'MarketCap', 'Close', 'Volume', 'Volume Spike']])
