import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Parameters
initial_capital = 100000
capital = initial_capital
start_date = "2013-01-01"
end_date = "2023-01-01"
capital_history = []
portfolio = []  # Each element is a dict: {symbol, buy_price, buy_date, quantity, weeks_held}
portfolio_value = 0

# Manually curated list of present + past Nifty 100 constituents
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
print(symbols)
# Get weekly dates
weekly_dates = pd.date_range(start=start_date, end=end_date, freq="W-FRI")

# Download data once
data = yf.download(
    tickers=symbols,
    start=start_date,
    end=end_date,
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    threads=True
)

# Backtest logic
for current_date in weekly_dates:
    # Ensure current_date exists in data
    for holding in portfolio[:]:
        try:
            # Look for the closest date if current_date is missing
            df = data[holding['symbol']].loc[:current_date]

            # If data for the current_date is missing, find the closest available date
            if current_date not in df.index:
                closest_date = df.index[df.index <= current_date].max()
                df = df.loc[closest_date:closest_date]

            # Calculate the short and long moving averages
            short_sma = df['Close'].rolling(window=50).mean()
            long_sma = df['Close'].rolling(window=200).mean()

            # Update weeks_held
            holding['weeks_held'] = (current_date - holding['buy_date']).days // 7  # Update weeks held

            # Check if there's a bearish crossover or 30% rally
            if len(short_sma) > 1 and len(long_sma) > 1:
                if short_sma.iloc[-1] < long_sma.iloc[-1] or df['Close'].iloc[-1] >= holding['buy_price'] * 1.20:
                    # Sell if either condition is met
                    capital += df['Close'].iloc[-1] * holding['quantity']
                    portfolio.remove(holding)
        except Exception as e:
            print(f"Error selling {holding['symbol']}: {e}")
            continue

    # Step 2: Check for golden crossover and buy
    for symbol in symbols:
        try:
            df = data[symbol].loc[:current_date]
            if len(df) < 200:
                continue

            # If data for the current_date is missing, find the closest available date
            if current_date not in df.index:
                closest_date = df.index[df.index <= current_date].max()
                df = df.loc[closest_date:closest_date]

            short_sma = df['Close'].rolling(window=50).mean()
            long_sma = df['Close'].rolling(window=200).mean()

            # Check for golden crossover
            if len(short_sma) > 1 and len(long_sma) > 1:
                if short_sma.iloc[-2] < long_sma.iloc[-2] and short_sma.iloc[-1] > long_sma.iloc[-1]:
                    # Buy when golden crossover happens
                    price_today = df['Close'].iloc[-1]
                    qty = int(1000 // price_today)  # Buy as much as possible with 1000
                    if capital >= price_today * qty:
                        capital -= price_today * qty
                        portfolio.append({"symbol": symbol, "buy_price": price_today, "quantity": qty, "buy_date": current_date, "weeks_held": 0})

        except Exception as e:
            print(f"Error buying {symbol}: {e}")
            continue

    # Track cash and stocks value in portfolio
    portfolio_value = sum([data[holding['symbol']].loc[current_date]['Close'] * holding['quantity'] for holding in portfolio if current_date in data[holding['symbol']].index])
    capital_history.append((current_date, capital + portfolio_value))

# Final capital
final_value = capital + sum([data[holding['symbol']].iloc[-1]['Close'] * holding['quantity'] for holding in portfolio if not data[holding['symbol']].empty])
n_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365
cagr = ((final_value / initial_capital) ** (1 / n_years)) - 1

# Print portfolio status
print("\nCurrent portfolio:")
print(f"Cash Position: ₹{capital:,.2f}")
for holding in portfolio:
    print(f"Stock: {holding['symbol']}, Quantity: {holding['quantity']}, Buy Price: ₹{holding['buy_price']}, Weeks Held: {holding['weeks_held']}")

print(f"\n📊 Final Portfolio Value (Including Cash): ₹{final_value:,.2f}")
print(f"📈 CAGR over {n_years:.2f} years: {cagr * 100:.2f}%")
