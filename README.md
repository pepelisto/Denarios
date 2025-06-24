# 🧠 Denarios – Modular Framework for Quantitative Crypto Trading

**Denarios** is a full-stack trading infrastructure built with Python and Django to research, simulate, and execute crypto futures trading strategies.  
It supports multi-timeframe analysis, backtesting with detailed metrics, and real-time trading via the Binance Futures API.

> This is not a toy bot. It's a flexible, production-grade framework to develop, validate, and iterate algorithmic trading ideas at scale.

---

## 🚀 Key Features

- 📉 **Multi-asset & Multi-timeframe support**  
  Backtest and execute strategies across BTC, ETH, SOL, XRP — or any asset available on Binance Futures.

- 🧠 **Strategy-agnostic architecture**  
  Plug any technical logic or indicator — dozens of strategies already tested using EMA, RSI, volume signals, engulfing candles, and more.

- 🧪 **Custom backtesting engine**  
  Simulates entry/exit conditions, stop loss, take profit, and trailing stops. Logs every trade to SQL for analytics.

- 📊 **Real-time visual analytics**  
  Built-in charts for drawdown, Sharpe ratio, profit factor, win/loss ratio — filterable by asset or strategy.

- 🤖 **Live execution-ready**  
  Two real-time bots (Agripina & Anastasia) manage entry and exits on Binance Futures using REST API with optional email alerts.

- ⚙️ **Modular indicator system**  
  Easily add indicators to any timeframe or asset using the `AddIndicators` module.

- 🗄️ **Database integration**  
  Trades (real or simulated) are logged into SQL via Django models for later querying and performance review.

---

## 🧱 Project Structure
```
Denarios/
├── app/                      # Django models for trades, simulations, strategies
├── templates/                # Web frontend for reviewing position history and stats
├── bots/
│   ├── simulaciones/         # Core simulation/backtesting logic
│   │   ├── A90/              # Most recent strategy logic
│   │   ├── snippets/         # Metrics & visualizations (drawdown, Sharpe, etc.)
│   ├── samples/
│   │   ├── CryptoGetSamples/ # Data download from Binance
│   │   ├── AddIndicators/    # Custom indicators for OHLCV data
│   ├── AA/ and AA9/          # Real-time bots
│   │   ├── Agripina.py       # Strategy execution & trade entry
│   │   ├── Anastasia.py      # TP/SL management & trade closure
│   ├── Funciones/            # Live loop, filters, time checks
├── CryptoAnalyzer/           # Binance connection, trade functions, price feed
├── BotsForex/                # (WIP) Future forex bot replication
└── settings/                 # Django configuration
```

---

## 📌 Tech Stack

- **Python 3**
- **Django**
- **Pandas / NumPy**
- **TA-Lib / `ta`**
- **Binance REST API (Futures)**
- **PostgreSQL / SQLite**
- **Matplotlib / Seaborn**
- **SMTP (email alerts)**

---

## 🧠 Why this matters

This project was built from scratch over years of experimentation. While it’s not currently profitable, it has been instrumental in learning how to:

- Design scalable, testable quant trading systems
- Automate market data ingestion, strategy execution, and reporting
- Evaluate performance with real metrics and visual feedback
- Iterate fast over dozens of strategies with minimal code changes

---

## ⚠️ Disclaimer

This system is for educational and research purposes. It does not guarantee returns. Use at your own risk when trading real funds.
