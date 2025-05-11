import yfinance as yf
import pandas as pd
from datetime import datetime

# Parameters
initial_capital = 100000
capital = initial_capital
start_date = "2000-05-01"
end_date = "2025-05-01"
weekly_buy = 500
weekly_sell = 1000

# Combined current + historical Nifty 100 constituents
symbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "ITC", "SBIN", "BHARTIARTL",
    "BAJFINANCE", "HCLTECH", "ASIANPAINT", "LT", "AXISBANK", "MARUTI", "SUNPHARMA", "TITAN", "WIPRO", "DMART",
    "ADANIENT", "ADANIPORTS", "ADANIGREEN", "BAJAJ-AUTO", "BAJAJFINSV", "BPCL", "CIPLA", "COALINDIA",
    "DIVISLAB", "DRREDDY", "EICHERMOT", "GRASIM", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "ICICIPRULI", "INDUSINDBK",
    "JSWSTEEL", "M&M", "NTPC", "ONGC", "POWERGRID", "SBILIFE", "SHREECEM", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TECHM", "ULTRACEMCO", "UPL", "VEDL", "BRITANNIA", "GAIL", "NAUKRI", "PIDILITIND", "AMBUJACEM", "APOLLOHOSP",
    "BAJAJHLDNG", "BERGEPAINT", "BOSCHLTD", "DABUR", "HAVELLS", "ICICIGI", "LUPIN", "PAGEIND",
    "PETRONET", "RECLTD", "SAIL", "SRF", "TORNTPHARM", "UBL", "BANDHANBNK", "BANKBARODA", "BHEL", "CANBK",
    "CHOLAFIN", "IDFCFIRSTB", "MANAPPURAM", "MFSL", "MRF", "NHPC", "PNB", "RAJESHEXPO", "RBLBANK", "SIEMENS",
     "TATACHEM", "TVSMOTOR", "ZEEL"
]
symbols = [symbol + ".NS" for symbol in symbols]

# Get weekly dates
weekly_dates = pd.date_range(start=start_date, end=end_date, freq="W-FRI")

# Download historical data
data = yf.download(
    tickers=symbols,
    start=start_date,
    end=end_date,
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    threads=True
)

# Initialize holdings
holdings = {symbol: 0 for symbol in symbols}

# Backtest loop
for date in weekly_dates:
    prev_week = date - pd.Timedelta(days=7)

    for symbol in symbols:
        try:
            df = data[symbol].loc[prev_week:date]
            if df.empty or len(df) < 2:
                continue

            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            change = ((end_price - start_price) / start_price) * 100

            if change <= -5 and capital >= weekly_buy:
                qty = int(weekly_buy // end_price)
                if qty > 0:
                    holdings[symbol] += qty
                    capital -= qty * end_price

            elif change >= 10 and holdings[symbol] > 0:
                qty = int(weekly_sell // end_price)
                qty = min(qty, holdings[symbol])
                if qty > 0:
                    holdings[symbol] -= qty
                    capital += qty * end_price

        except Exception as e:
            print(f"⚠️ {symbol} failed: {e}")
            continue

# Final value of holdings
final_prices = {}
for symbol in symbols:
    try:
        final_prices[symbol] = data[symbol].loc[end_date]['Close']
    except:
        final_prices[symbol] = 0

holding_value = sum(holdings[symbol] * final_prices.get(symbol, 0) for symbol in symbols)
portfolio_value = capital + holding_value

# Calculate CAGR
n_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
cagr = ((portfolio_value / initial_capital) ** (1 / n_years)) - 1

print(f"\n💰 Final Capital: ₹{capital:,.2f}")
print(f"📦 Holding Value: ₹{holding_value:,.2f}")
print(f"📊 Total Portfolio Value: ₹{portfolio_value:,.2f}")
print(f"📈 CAGR over {n_years:.2f} years: {cagr * 100:.2f}%")
