import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Parameters
initial_capital = 100000
capital = initial_capital
start_date = "2022-01-01"
end_date = "2025-01-01"
rebalance_frequency = "M"  # Monthly rebalance
capital_history = []
portfolio = []  # [{symbol, quantity, buy_price, buy_date}]
portfolio_value = 0

# Sample fundamental data with symbols (ensure .NS suffix)
fundamentals = pd.DataFrame({
    'symbol': ['INFY.NS', 'TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS'],
    'ROCE': [18, 22, 17, 16],
    'revenue_growth': [12, 10, 15, 11]
})

# Filter for quality
quality_stocks = fundamentals[
    (fundamentals['ROCE'] > 15) & (fundamentals['revenue_growth'] > 10)
]['symbol'].tolist()

# Download historical data
data = yf.download(
    tickers=quality_stocks,
    start=start_date,
    end=end_date,
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    threads=True
)

# Generate rebalance dates
rebalance_dates = pd.date_range(start=start_date, end=end_date, freq=rebalance_frequency)

# Backtest
for current_date in rebalance_dates:
    # Sell logic: after 3 months or stop loss
    for holding in portfolio[:]:
        df = data[holding['symbol']].loc[:current_date]
        if len(df) < 1 or current_date not in df.index:
            continue
        price_today = df.loc[current_date]['Close']
        weeks_held = (current_date - holding['buy_date']).days // 7

        if weeks_held >= 12 or price_today < holding['buy_price'] * 0.9:
            capital += price_today * holding['quantity']
            portfolio.remove(holding)

    # Calculate momentum (6-month return)
    momentum_scores = []
    for symbol in quality_stocks:
        df = data[symbol].loc[:current_date]
        if len(df) < 126:
            continue
        if current_date not in df.index:
            continue
        price_now = df.loc[current_date]['Close']
        price_6mo_ago = df.iloc[-126]['Close']
        momentum = (price_now - price_6mo_ago) / price_6mo_ago
        # Avoid recent 15% drop from peak
        peak = df['Close'].rolling(window=90).max().iloc[-1]
        if price_now >= 0.85 * peak:
            momentum_scores.append((symbol, momentum))

    # Rank and pick top 5
    top_momentum = sorted(momentum_scores, key=lambda x: x[1], reverse=True)[:5]

    for symbol, _ in top_momentum:
        df = data[symbol].loc[:current_date]
        if len(df) < 1 or current_date not in df.index:
            continue
        price_today = df.loc[current_date]['Close']
        qty = int((capital / len(top_momentum)) // price_today)
        if qty > 0:
            capital -= qty * price_today
            portfolio.append({
                'symbol': symbol,
                'buy_price': price_today,
                'quantity': qty,
                'buy_date': current_date
            })

    # Track portfolio value
    total_value = capital
    for holding in portfolio:
        df = data[holding['symbol']]
        if current_date not in df.index:
            continue
        price = df.loc[current_date]['Close']
        total_value += price * holding['quantity']
    capital_history.append((current_date, total_value))

# Final portfolio valuation
final_value = capital
for holding in portfolio:
    df = data[holding['symbol']]
    final_price = df.iloc[-1]['Close']
    final_value += final_price * holding['quantity']

n_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
cagr = ((final_value / initial_capital) ** (1 / n_years)) - 1

# Print holdings
print("Final Holdings:")
for holding in portfolio:
    weeks = (pd.to_datetime(end_date) - holding['buy_date']).days // 7
    print(f"{holding['symbol']}: Qty={holding['quantity']} | Buy=₹{holding['buy_price']:.2f} | Held {weeks} weeks")

print(f"\n💰 Final Portfolio Value: ₹{final_value:,.2f}")
print(f"📈 CAGR: {cagr * 100:.2f}%")

# Visualization
history_df = pd.DataFrame(capital_history, columns=["Date", "Total Value"])
plt.figure(figsize=(12, 6))
plt.plot(history_df["Date"], history_df["Total Value"], label="Portfolio Value", color="blue")
plt.title("Portfolio Value Over Time")
plt.xlabel("Date")
plt.ylabel("Value (₹)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
