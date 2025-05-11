import time
import sys
from kiteconnect import KiteConnect
import pandas as pd
import yfinance as yf

# ----------------------------
# Zerodha API Credentials
api_key = "8qq6ag2yl1bb582t"
api_secret = "odxrjws6dyxxa8hl0nqpdtvkmqz0tfx7"
kite = KiteConnect(api_key=api_key)
# ----------------------------

# STEP 1: Authenticate and get access token
print("🔗 Login URL:", kite.login_url())
print("⚠️  Open the above URL in your browser and complete the login.")
request_token = input("🔑 Paste request_token from redirect URL: ").strip()

if not request_token or request_token.lower().startswith("failed"):
    print("❌ Request token not found. Exiting in 5 seconds.")
    time.sleep(5)
    sys.exit()

try:
    session_data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = session_data["access_token"]
    kite.set_access_token(access_token)

    with open("access_token.txt", "w") as f:
        f.write(access_token)

    print("✅ Access token saved.")

except Exception as e:
    print("❌ Error in authentication:", e)
    sys.exit()

# STEP 2: Get Nifty 200 stock list
try:
    nifty_200 = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty200list.csv")
    symbols = nifty_200['Symbol'].tolist()
except Exception as e:
    print("❌ Failed to download Nifty 200 list:", e)
    sys.exit()

print(f"📈 Checking {len(symbols)} stocks...")

# STEP 3: Loop through each stock
buy_candidates = []
sell_candidates = []

for symbol in symbols:
    try:
        stock = yf.Ticker(symbol + ".NS")
        hist = stock.history(period="7d", interval="1d")

        if len(hist) < 2:
            continue

        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]

        change_percent = ((end_price - start_price) / start_price) * 100

        if change_percent <= -5:
            buy_candidates.append((symbol, change_percent))
        elif change_percent >= 10:
            sell_candidates.append((symbol, change_percent))

        time.sleep(0.2)  # To avoid rate limits

    except Exception as e:
        print(f"⚠️ Error fetching data for {symbol}: {e}")

# STEP 4: Place buy orders
for symbol, change in buy_candidates:
    try:
        ltp = kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]['last_price']
        qty = int(500 // ltp)
        if qty > 0:
            kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol=symbol,
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=qty,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_CNC
            )
            print(f"🟢 BUY: {symbol} ({change:.2f}%) — {qty} shares (~₹500)")
    except Exception as e:
        print(f"❌ Failed to BUY {symbol}: {e}")

# STEP 5: Place sell orders
for symbol, change in sell_candidates:
    try:
        ltp = kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]['last_price']
        qty = int(1000 // ltp)
        if qty > 0:
            kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol=symbol,
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=qty,
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_CNC
            )
            print(f"🔴 SELL: {symbol} ({change:.2f}%) — {qty} shares (~₹1000)")
    except Exception as e:
        print(f"❌ Failed to SELL {symbol}: {e}")