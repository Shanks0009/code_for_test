import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)

def get_fundamentals(symbol):
    stock = yf.Ticker(symbol)
    try:
        fin = stock.financials
        bs = stock.balance_sheet
        if fin.empty or bs.empty:
            return None, None

        EBIT = fin.loc['EBIT'].iloc[0]
        TotalAssets = bs.loc['Total Assets'].iloc[0]
        CurrentLiabilities = bs.loc['Current Liabilities'].iloc[0]
        CapitalEmployed = TotalAssets - CurrentLiabilities
        ROCE = (EBIT / CapitalEmployed) * 100 if CapitalEmployed != 0 else None

        rev_growth = None
        if 'Total Revenue' in fin.index:
            rev_series = fin.loc['Total Revenue']
            if len(rev_series) >= 2:
                rev_growth = ((rev_series.iloc[0] - rev_series.iloc[1]) / rev_series.iloc[1]) * 100
        return ROCE, rev_growth
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
        return None, None

def get_momentum(symbol, end_date):
    stock = yf.Ticker(symbol)
    start_date = end_date - timedelta(days=180)
    hist = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    if hist.empty or len(hist['Close']) < 2:
        return None, None, None
    momentum = (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100
    drawdown = (hist['Close'].max() - hist['Close'][-1]) / hist['Close'].max() * 100
    return momentum, drawdown, hist

def analyze_stocks(symbols):
    today = datetime.today()
    recommendation = []

    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        ROCE, rev_growth = get_fundamentals(symbol)
        momentum, drawdown, hist = get_momentum(symbol, today)

        if ROCE is None or momentum is None:
            print(f"Insufficient data for {symbol}")
            continue

        verdict = "BUY" if (
            ROCE > 15 and 
            (rev_growth is None or rev_growth > 10) and 
            momentum > 0 and 
            drawdown < 15
        ) else "DO NOT BUY"

        recommendation.append({
            "Symbol": symbol,
            "ROCE (%)": round(ROCE, 2),
            "Revenue Growth (%)": round(rev_growth, 2) if rev_growth else "N/A",
            "6M Momentum (%)": round(momentum, 2),
            "Drawdown from peak (%)": round(drawdown, 2),
            "Verdict": verdict
        })
        """""
        if hist is not None and not hist.empty:
            plt.figure(figsize=(10, 4))
            plt.plot(hist.index, hist['Close'], label=symbol)
            plt.title(f'{symbol} - 6 Month Price Chart')
            plt.xlabel("Date")
            plt.ylabel("Price (₹)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        """""
    df = pd.DataFrame(recommendation)
    df.to_csv("stock_analysis_report.csv", index=False)
    return df
# Replace these symbols with any you'd like to analyze
symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'BAJFINANCE.NS', 'HCLTECH.NS', 'ASIANPAINT.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'WIPRO.NS', 'DMART.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'ADANIGREEN.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BPCL.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GRASIM.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'ICICIPRULI.NS', 'INDUSINDBK.NS', 'JSWSTEEL.NS', 'M&M.NS', 'NTPC.NS', 'ONGC.NS', 'POWERGRID.NS', 'SBILIFE.NS', 'SHREECEM.NS', 'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'ULTRACEMCO.NS', 'UPL.NS', 'VEDL.NS', 'BRITANNIA.NS', 'GAIL.NS', 'NAUKRI.NS', 'PIDILITIND.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS', 'BAJAJHLDNG.NS', 'BERGEPAINT.NS', 'BOSCHLTD.NS', 'DABUR.NS', 'HAVELLS.NS', 'ICICIGI.NS', 'LUPIN.NS', 'PAGEIND.NS', 'PETRONET.NS', 'RECLTD.NS', 'SAIL.NS', 'SRF.NS', 'TORNTPHARM.NS', 'UBL.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BHEL.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'IDFCFIRSTB.NS', 'MANAPPURAM.NS', 'MFSL.NS', 'MRF.NS', 'NHPC.NS', 'PNB.NS', 'RAJESHEXPO.NS', 'RBLBANK.NS', 'SIEMENS.NS', 'TATACHEM.NS', 'TVSMOTOR.NS', 'ZEEL.NS']

print(analyze_stocks(symbols))
