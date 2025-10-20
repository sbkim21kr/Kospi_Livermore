import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from datetime import datetime
import shutil

# --- Livermore Metrics ---
def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def livermore_metrics(df):
    df['Volume Spike'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df['Momentum'] = df['Close'] - df['Close'].shift(5)
    df['RSI'] = compute_rsi(df['Close'])
    return df

# --- Load All KOSPI Stocks ---
kospi = fdr.StockListing('KRX')
kospi = kospi[kospi['Market'] == 'KOSPI']

# --- Handle missing columns gracefully ---
columns = ['Code', 'Name', 'Marcap']
if 'Sector' in kospi.columns:
    columns.append('Sector')
kospi = kospi[columns].dropna()

# --- Prepare Output ---
results = []
failed = []

# --- Worker Function ---
def process_stock(row):
    code = row['Code']
    name = row['Name']
    sector = row.get('Sector', 'Unknown')
    marcap = row['Marcap']
    try:
        df = fdr.DataReader(code, '2023-01-01')
        if len(df) < 50:
            return None
        df = livermore_metrics(df)
        latest = df.iloc[-1]
        return {
            'Code': code,
            'Name': name,
            'Sector': sector,
            'MarketCap': marcap,
            'Close': latest['Close'],
            'Volume': latest['Volume'],
            'Volume Spike': round(latest['Volume Spike'], 2),
            'Momentum': round(latest['Momentum'], 2),
            'RSI': round(latest['RSI'], 2),
        }
    except Exception as e:
        return {'failed': code, 'error': str(e)}

# --- Parallel Execution with Progress Bar ---
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_stock, row): row for _, row in kospi.iterrows()}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing KOSPI stocks"):
        result = future.result()
        if result is None:
            continue
        if 'failed' in result:
            failed.append(result)
        else:
            results.append(result)

# --- Save Main CSV ---
df_all = pd.DataFrame(results)
df_all.to_csv('latest_kospi.csv', index=False)

# --- Archive to data/ folder with timestamp ---
today = datetime.today().strftime('%Y%m%d')
os.makedirs('data', exist_ok=True)
shutil.copy('latest_kospi.csv', f'data/kospi_{today}.csv')

# --- Save Failed Tickers ---
if failed:
    pd.DataFrame(failed).to_csv('failed_tickers.csv', index=False)
    print(f"⚠️ {len(failed)} tickers failed. See failed_tickers.csv for details.")

# --- Split by Sector ---
os.makedirs('sectors', exist_ok=True)
if 'Sector' in df_all.columns:
    for sector, group in df_all.groupby('Sector'):
        filename = f"sectors/{sector.replace('/', '_').replace(' ', '_')}.csv"
        group.to_csv(filename, index=False)

# --- Split by Market Cap Tier ---
os.makedirs('tiers', exist_ok=True)
df_all['Tier'] = pd.qcut(df_all['MarketCap'], q=3, labels=['Small Cap', 'Mid Cap', 'Large Cap'])
for tier, group in df_all.groupby('Tier'):
    group.to_csv(f"tiers/{tier.replace(' ', '_')}.csv", index=False)

print("✅ Screener complete. Data saved to latest_kospi.csv, data/, sectors/, tiers/, and failed_tickers.csv (if any).")
