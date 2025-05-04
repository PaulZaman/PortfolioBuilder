from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.firebase_init import db
from app.core.firebase_auth import verify_token
import uuid
from app.services.yfinance_service import get_stock_data
from app.models.portfolio import Portfolio
from app.core.firebase_watchlist import get_all_stocks_firebase
from app.core.firebase_portfolio import create_new_portfolio_firebase, get_user_portfolios_firebase, delete_portfolio_firebase, get_portfolio_firebase
from app.optimizitation.optimize import optimize_portfolio
import datetime


router = APIRouter(prefix="/api/portfolios", tags=["Portfolios"])

@router.post("/optimize")
async def optimize_new_portfolio(

    data: dict = Body(...),
    user=Depends(verify_token)
):
    try:
        
        uid = user["localId"]

        tickers = data.get("tickers", [])
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        interval = data.get("interval", "1d")
        metric = data.get("metric", "sharpe")
        allow_short = data.get("allow_short", False)

        if not start_date:
            raise HTTPException(status_code=422, detail="start_date is required")

        result = optimize_portfolio(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            metric=metric,
            allow_short=allow_short,
        )

        return {
            "tickers": tickers,
            "optimized_weights": result["weights"],
            "metric": metric,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Optimization error: {str(e)}")

@router.post("/optimize/{ptfid}")
async def optimize_existing_portfolio(
    ptfid: str,
    data: dict = Body(...),
    user=Depends(verify_token)
):
    try:
        
        uid = user["localId"]
        portfolio = await get_portfolio_firebase(ptfid)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        tickers = portfolio.get("tickers", [])
        name = portfolio.get("name", "Unnamed")

        if not tickers:
            raise HTTPException(status_code=400, detail="No tickers in this portfolio.")

        # Récupération des champs du body JSON
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        interval = data.get("interval", "1d")
        metric = data.get("metric", "sharpe")
        allow_short = data.get("allow_short", False)

        if not start_date:
            raise HTTPException(status_code=422, detail="start_date is required")

        result = optimize_portfolio(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            metric=metric,
            allow_short=allow_short,
        )

        return {
            "portfolio_name": name,
            "tickers": tickers,
            "optimized_weights": result["weights"],
            "metric": metric,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Optimization error: {str(e)}")

@router.post("/create")
async def create_portfolio(portfolio: Portfolio, user=Depends(verify_token)):
    try:
        uid = user["localId"]

        # Make sure the tickers are valid
        available_stocks = await get_all_stocks_firebase()
        available_tickers = [stock["ticker"] for stock in available_stocks]
        for ticker in portfolio.tickers:
            if ticker not in available_tickers:
                raise HTTPException(status_code=400, detail=f"Ticker {ticker} is not available")
        
        # Make sure the weights sum to 1
        if sum(portfolio.weights) != 1:
            raise HTTPException(status_code=400, detail="Weights must sum to 1")
        
        # Make sure there are no duplicate tickers
        if len(portfolio.tickers) != len(set(portfolio.tickers)):
            raise HTTPException(status_code=400, detail="Duplicate tickers found")
        
        # Make sure the start date is before today
        if portfolio.start_date > datetime.datetime.now().date():
            raise HTTPException(status_code=400, detail="Start date cannot be in the future")
        
        # Make sure there are as many weights as tickers
        if len(portfolio.tickers) != len(portfolio.weights):
            raise HTTPException(status_code=400, detail="Number of weights must match number of tickers")
        
        # Get the porformance of the tickers
        performances = get_stock_data(portfolio.tickers, start_date=portfolio.start_date)

        # Multiply the performance by the weights
        performances['ptf'] = performances[portfolio.tickers].multiply(portfolio.weights, axis=1).sum(axis=1)

        # Create a new portfolio in Firebase Firestore
        ptfid = str(uuid.uuid4())
        ptf = await create_new_portfolio_firebase(
            uid, ptfid, portfolio.tickers, portfolio.weights, performances['Date'].tolist(), performances['ptf'].tolist(), portfolio.name)

        # Return the portfolio data
        return {"message": "Portfolio created successfully", "portfolio": ptf}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating portfolio: {str(e)}")

@router.get("/get")
async def get_user_portfolios(user=Depends(verify_token)):
    try:
        uid = user["localId"]
        portfolios = await get_user_portfolios_firebase(uid)
        return {"portfolios": portfolios}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching portfolios: {str(e)}")
    
@router.delete("/delete/{ptfid}")
async def delete_portfolio(ptfid: str, user=Depends(verify_token)):
    try:
        uid = user["localId"]
        await delete_portfolio_firebase(uid, ptfid)
        return {"message": "Portfolio deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting portfolio: {str(e)}")
    
@router.get("/get/{ptfid}")
async def get_portfolio(ptfid: str, user=Depends(verify_token)):
    try:
        uid = user["localId"]
        portfolio = await get_portfolio_firebase(ptfid)
        return {"portfolio": portfolio}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching portfolio: {str(e)}")
