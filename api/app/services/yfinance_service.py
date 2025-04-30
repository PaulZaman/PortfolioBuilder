import yfinance as yf
import pandas as pd

def get_daily_performance(tickers):
    try:
        data = yf.download(tickers, period="2d", group_by='ticker', auto_adjust=False)
        performance = {}

        for ticker in tickers:
            try:
                close_prices = data[ticker]["Close"]
                if len(close_prices) < 2:
                    performance[ticker] = None
                    continue

                prev_close = close_prices.iloc[-2]
                last_close = close_prices.iloc[-1]
                change = ((last_close - prev_close) / prev_close) * 100
                performance[ticker] = round(change, 2)
            except Exception:
                performance[ticker] = None

            # Check if the performance is not nan, if so, replace it with None
            if performance[ticker] is not None and (performance[ticker] != performance[ticker]):
                performance[ticker] = None

        return performance

    except Exception:
        return {ticker: None for ticker in tickers}
    
def get_stock_data(tickers, start_date=None, end_date=None):
    try:
        # If start date is not none, remove 1 day from it
        if start_date is not None:
            start_date = pd.to_datetime(start_date) - pd.Timedelta(days=1)
            start_date = start_date.strftime("%Y-%m-%d")

        data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', auto_adjust=False)

        if isinstance(tickers, str):
            # Single ticker
            data = data[['Close']].reset_index()
            data = data.rename(columns={'Close': tickers})
        else:
            # Multiple tickers
            close_data = pd.DataFrame()
            for ticker in tickers:
                ticker_close = data[ticker]['Close'].rename(ticker)
                close_data[ticker] = ticker_close
            close_data = close_data.reset_index()
            data = close_data
        
        # convert to daily performance
        for ticker in data.columns[1:]:
            data[ticker] = data[ticker].pct_change()
            data[ticker] = data[ticker].round(8)

        # Dropna
        data = data.dropna()

        return data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None