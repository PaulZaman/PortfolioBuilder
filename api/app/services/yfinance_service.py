import yfinance as yf

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

        return performance

    except Exception:
        return {ticker: None for ticker in tickers}
