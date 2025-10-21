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

### 📈 What Do the Arrows Mean?
Arrows in the **Trend Arrow** column show the 20-day price trend:
- ⬆️ Upward: Price is rising
- ⬇️ Downward: Price is falling
- ➡️ Sideways: Price is stable
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

# --- Ensure numeric columns ---
for col in ['MarketCap', 'Volume', 'Close', 'Volume Spike', '20-day Avg Close']:
    filtered[col] = pd.to_numeric(filtered[col], errors='coerce')

# --- Add raw columns for sorting ---
filtered['MarketCap_raw'] = filtered['MarketCap']
filtered['Volume_raw'] = filtered['Volume']
filtered['Close_raw'] = filtered['Close']
filtered['Volume Spike_raw'] = filtered['Volume Spike']

# --- Format display columns ---
filtered['MarketCap'] = filtered['MarketCap_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
filtered['Volume'] = filtered['Volume_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
filtered['Close'] = filtered['Close_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")

# --- Add Trend Arrow column ---
def get_arrow(row):
    if pd.isna(row['Close_raw']) or pd.isna(row['20-day Avg Close']):
        return ""
    change = (row['Close_raw'] - row['20-day Avg Close']) / row['20-day Avg Close']
    return "⬆️" if change > 0.03 else "⬇️" if change < -0.03 else "➡️"

filtered['Trend Arrow'] = filtered.apply(get_arrow, axis=1)

# --- Display Breakout Stocks ---
st.markdown("### 📋 Breakout Stocks")
st.dataframe(
    filtered[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike']],
    use_container_width=True
)

# --- Top 5 Volume Spikes ---
st.markdown("### 🔥 Top 5 Volume Spikes Today")
top5 = filtered.sort_values(by='Volume Spike_raw', ascending=False).head(5)
st.dataframe(
    top5[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike']],
    use_container_width=True
)

# --- Download as TXT with Timestamp and Top 5 ---
header = f"KOSPI Livermore Screener — Volume Spike Filter\nData retrieved at: {timestamp} KST\n\n"

main_table = filtered[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike']].to_string(index=False)
top5_table = top5[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike']].to_string(index=False)

txt_output = (
    header +
    "🔥 Top 5 Volume Spikes Today:\n" +
    top5_table +
    "\n\n📋 All Filtered Results:\n" +
    main_table
)

st.download_button(
    label="📥 Download Filtered Results as TXT",
    data=txt_output.encode('utf-8'),
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
        for col in ['MarketCap', 'Volume', 'Close', '20-day Avg Close']:
            archive_df[col] = pd.to_numeric(archive_df[col], errors='coerce')
        archive_df['MarketCap_raw'] = archive_df['MarketCap']
        archive_df['Volume_raw'] = archive_df['Volume']
        archive_df['Close_raw'] = archive_df['Close']
        archive_df['Volume Spike_raw'] = archive_df['Volume Spike']
        archive_df['MarketCap'] = archive_df['MarketCap_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Volume'] = archive_df['Volume_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Close'] = archive_df['Close_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Trend Arrow'] = archive_df.apply(get_arrow, axis=1)
        st.dataframe(
            archive_df[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike']],
            use_container_width=True
        )
