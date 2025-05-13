import yfinance as yf
import pandas as pd

# Define your universe of stocks (e.g., S&P 500 or NASDAQ-100 tickers)
# You can get a more complete list from a CSV, but we'll use a short sample here
tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'BAJFINANCE.NS', 'HCLTECH.NS', 'ASIANPAINT.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'WIPRO.NS', 'DMART.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'ADANIGREEN.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BPCL.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GRASIM.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'ICICIPRULI.NS', 'INDUSINDBK.NS', 'JSWSTEEL.NS', 'M&M.NS', 'NTPC.NS', 'ONGC.NS', 'POWERGRID.NS', 'SBILIFE.NS', 'SHREECEM.NS', 'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'ULTRACEMCO.NS', 'UPL.NS', 'VEDL.NS', 'BRITANNIA.NS', 'GAIL.NS', 'NAUKRI.NS', 'PIDILITIND.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'BAJAJHLDNG.NS', 'BERGEPAINT.NS', 'BOSCHLTD.NS', 'DABUR.NS', 'HAVELLS.NS', 'ICICIGI.NS', 'LUPIN.NS', 'PAGEIND.NS', 'PETRONET.NS', 'RECLTD.NS', 'SAIL.NS', 'SRF.NS', 'TORNTPHARM.NS', 'UBL.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BHEL.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'IDFCFIRSTB.NS', 'MANAPPURAM.NS', 'MFSL.NS', 'MRF.NS', 'NHPC.NS', 'PNB.NS', 'RAJESHEXPO.NS', 'RBLBANK.NS', 'SIEMENS.NS', 'TATACHEM.NS', 'TVSMOTOR.NS', 'ZEEL.NS']

# Screener results
results = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        pe_ratio = info.get('trailingPE', None)
        peg_ratio = info.get('pegRatio', None)
        earnings_growth = info.get('earningsQuarterlyGrowth', None)

        hist = stock.history(period='3mo')
        if hist.empty:
            continue
        
        price_3mo_ago = hist['Close'].iloc[0]
        current_price = hist['Close'].iloc[-1]
        momentum = (current_price - price_3mo_ago) / price_3mo_ago * 100

        if (
            pe_ratio is not None and pe_ratio < 25 and
            peg_ratio is not None and peg_ratio < 1.5 and
            earnings_growth is not None and earnings_growth > 0.10 and
            momentum > 5
        ):
            results.append({
                'Ticker': ticker,
                'P/E': pe_ratio,
                'PEG': peg_ratio,
                'Earnings Growth': earnings_growth,
                '3-Month Momentum (%)': round(momentum, 2)
            })
    except Exception as e:
        print(f"Error processing {ticker}: {e}")

df = pd.DataFrame(results)

if not df.empty:
    df = df.sort_values(by='3-Month Momentum (%)', ascending=False).reset_index(drop=True)
    df.to_csv("potential_gainers.csv", index=False)
    print("\nPotential Gainers saved to 'potential_gainers.csv':")
    print(df)
else:
    print("No stocks met the screener criteria.")