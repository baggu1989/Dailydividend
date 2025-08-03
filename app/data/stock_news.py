import os

import yfinance as yf
import logging

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_index_change(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="2d")
        if data.shape[0] < 2:
            logger.warning(f"Not enough data for {symbol}")
            return None
        prev_close = data['Close'].iloc[-2]
        current = data['Close'].iloc[-1]
        change = ((current - prev_close) / prev_close) * 100
        logger.info(f"{symbol} change: {change:.2f}%")
        return change
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

if __name__ == '__main__':
    sp500_change = get_index_change("^GSPC")
    eurostoxx_change = get_index_change("^STOXX50E")
    ftse100_change = get_index_change("^FTSE")

    logger.info({
        "S&P 500": sp500_change,
        "EUROSTOXX 50": eurostoxx_change,
        "FTSE 100": ftse100_change
    })
