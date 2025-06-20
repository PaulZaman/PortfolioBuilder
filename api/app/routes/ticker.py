# app/api/tickers.py

from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_auth import verify_token
from app.core.firebase_watchlist import get_all_stocks_firebase
from app.services.yfinance_service import get_info, get_stock_data
from datetime import datetime, timedelta
import yfinance as yf


router = APIRouter(prefix="/api/tickers", tags=["Tickers"])

@router.get("/info/{ticker}")
async def get_ticker_info(ticker: str, user=Depends(verify_token)):
	try:
		# Validate ticker
		available_stocks = await get_all_stocks_firebase()
		available_tickers = [stock["ticker"] for stock in available_stocks]
		
		if ticker not in available_tickers:
			raise HTTPException(status_code=400, detail=f"Ticker {ticker} is not available")

		# Fetch and return info
		return get_info(ticker)

	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Error fetching ticker info: {str(e)}")


@router.get("/hist/{ticker}")
async def get_ticker_history(
	ticker: str,
	user=Depends(verify_token)
):
	try:
		# Validate ticker
		available_stocks = await get_all_stocks_firebase()
		available_tickers = [stock["ticker"] for stock in available_stocks]
		if ticker not in available_tickers:
			raise HTTPException(status_code=400, detail=f"Ticker {ticker} is not available")

		# Calculate date range: last 30 days
		end_date = datetime.now().date()
		start_date = end_date - timedelta(days=30)

		# Fetch historical data using yfinance directly
		stock = yf.Ticker(ticker)
		hist = stock.history(start=start_date, end=end_date)

		# Check if data is empty
		if hist.empty:
			raise HTTPException(status_code=404, detail=f"No historical data found for {ticker}")

		# Return closing prices
		return {
			"ticker": ticker,
			"dates": hist.index.strftime('%Y-%m-%d').tolist(),
			"prices": hist['Close'].tolist()
		}

	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Error fetching ticker history: {str(e)}")