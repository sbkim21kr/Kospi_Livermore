# 🇰🇷 KOSPI Livermore Screener

![Auto-refresh KOSPI Screener](https://github.com/sbkim21/kospi-livermore/actions/workflows/refresh.yml/badge.svg)

Track breakout momentum across KOSPI stocks using Livermore-style volume logic.  
This dashboard automatically refreshes daily and highlights stocks with unusual volume spikes — a classic sign of accumulation or breakout behavior.

---

## 📊 Dashboard Features

- **Volume Spike Filter**: See which stocks are trading at 2x+ their average volume
- **Clean TXT Download**: Export filtered results for easy viewing on mobile
- **Historical Snapshots**: Browse past breakout candidates by date
- **Auto-updated CSVs**: GitHub Actions refreshes data daily at 17:00 KST

---

## 🧠 What Is Volume Spike?

Volume Spike measures how much today’s trading volume exceeds the average over the past 20 days:

```
Volume Spike = Today's Volume ÷ 20-day Average Volume
```

A value above **2.0** suggests unusual trading activity — often a sign of accumulation or breakout behavior.

---

## 🚀 How It Works

- `refresh.py`: Fetches KOSPI stock data and calculates volume metrics
- `dashboard.py`: Streamlit app for filtering, viewing, and downloading results
- `.github/workflows/refresh.yml`: GitHub Actions workflow that auto-refreshes data daily

---

## 📦 Tech Stack

- Python 3.12
- [uv](https://github.com/astral-sh/uv) for dependency management
- Streamlit for dashboard UI
- GitHub Actions for automation

---

## 🛠 Local Setup

```bash
uv venv
uv pip install -r pyproject.toml
streamlit run dashboard.py
```

---

## 📅 Auto-Refresh Schedule

- Runs daily at **08:00 UTC** (17:00 KST)
- Updates:
  - `latest_kospi.csv`
  - `data/` snapshots
  - `sectors/`, `tiers/`, `failed_tickers.csv`

---

## ✨ Author

**Sangbum Kim**  
📍 Incheon, South Korea  
🔗 [GitHub Profile](https://github.com/sbkim21)

---

## 📜 License

This project is open-source under the MIT License.
```

---

