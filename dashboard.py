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

# --- Top 5 Volume Spikes ---
st.markdown("### 🔥 Top 5 Volume Spikes Today")
top5 = filtered.sort_values(by='Volume Spike_raw', ascending=False).head(5)
top5_display = top5.copy()
top5_display['MarketCap'] = top5_display['MarketCap_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
top5_display['Volume'] = top5_display['Volume_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
top5_display['Close'] = top5_display['Close_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
top5_display['Volume Spike'] = top5_display['Volume Spike_raw'].round(2)

st.dataframe(
    top5_display[['Code', 'Name', 'MarketCap_raw', 'Close_raw', 'Trend Direction', 'Volume_raw', 'Volume Spike_raw']]
    .rename(columns={
        'MarketCap_raw': 'MarketCap',
        'Close_raw': 'Close',
        'Volume_raw': 'Volume',
        'Volume Spike_raw': 'Volume Spike'
    }),
    use_container_width=True
)

# --- Download as TXT with Timestamp and Top 5 ---
header = f"KOSPI Livermore Screener — Volume Spike Filter\nData retrieved at: {timestamp} KST\n\n"

main_table = display_df[['Code', 'Name', 'MarketCap', 'Close', 'Trend Direction', 'Volume', 'Volume Spike']].to_string(index=False)
top5_table = top5_display[['Code', 'Name', 'MarketCap', 'Close', 'Trend Direction', 'Volume', 'Volume Spike']].to_string(index=False)

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
        for col in ['MarketCap', 'Volume', 'Close', 'Volume Spike', '20-day Avg Close']:
            if col in archive_df.columns:
                archive_df[col] = pd.to_numeric(archive_df[col], errors='coerce')
        for col in ['MarketCap', 'Volume', 'Close', 'Volume Spike']:
            raw_col = f"{col}_raw"
            if col in archive_df.columns:
                archive_df[raw_col] = archive_df[col]
        archive_df['Trend Direction'] = archive_df.apply(get_trend, axis=1)
        archive_df['MarketCap'] = archive_df['MarketCap_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Volume'] = archive_df['Volume_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Close'] = archive_df['Close_raw'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "")
        archive_df['Volume Spike'] = archive_df['Volume Spike_raw'].round(2)

        st.dataframe(
            archive_df[['Code', 'Name', 'MarketCap_raw', 'Close_raw', 'Trend Direction', 'Volume_raw', 'Volume Spike_raw']]
            .rename(columns={
                'MarketCap_raw': 'MarketCap',
                'Close_raw': 'Close',
                'Volume_raw': 'Volume',
                'Volume Spike_raw': 'Volume Spike'
            }),
            use_container_width=True
        )
