import yfinance as yf
import os
import requests

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY") 

def get_index_change(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    res = requests.get(url).json()
    current = res.get("c")  
    prev_close = res.get("pc") 
    if current is None or prev_close is None:
        return None
    return ((current - prev_close) / prev_close) * 100

if __name__== '__main__':
    sp500_change = get_index_change("^GSPC")
    eurostoxx_change = get_index_change("^STOXX50E")
    ftse100_change = get_index_change("^FTSE")

    print({
        "S&P 500": sp500_change,
        "EUROSTOXX 50": eurostoxx_change,
        "FTSE 100": ftse100_change
    })
