from fastapi import APIRouter, Depends
from app.models.user import UserSignup, UserLogin
from app.core.firebase import signup_user, login_user, verify_token
from app.core.firebase import signup_user, db
from app.core.firebase import login_user, verify_token
from fastapi import HTTPException
import logging
from app.services.yfinance_service import get_daily_performance

# Configure logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Authentication"])

@router.post("/signup")
async def signup(user: UserSignup):
    try:
        logger.info(f"Attempting to sign up user with email: {user.email}")
        
        # Sign up the user with Firebase
        created_user = signup_user(user.email, user.password)
        logger.info("Firebase signup successful")

        # Firebase returns localId = UID
        uid = created_user['localId']

        # Save extra info (first name, last name) in Firestore
        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        logger.info(f"Saving user data to Firestore: {user_data}")
        
        db.collection("users").document(uid).set(user_data)
        logger.info("User data saved to Firestore successfully")
        
        return {
            "message": "User created successfully",
            "token": created_user["idToken"],
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login(user: UserLogin):
    try:
        logger.info(f"Attempting to login user with email: {user.email}")
        logged_in_user = login_user(user.email, user.password)
        logger.info("Login successful")
        return {"message": "Login successful", "token": logged_in_user["idToken"]}
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/protected")
async def protected_route(user=Depends(verify_token)):
    return {"message": f"Welcome, {user['email']}! You are authenticated."}

@router.get("/user-info")
async def get_user_info(user=Depends(verify_token)):
    try:
        uid = user["localId"]  # Firebase UID
        logger.info(f"Fetching user info for UID: {uid}")

        # Fetch user document from Firestore
        doc_ref = db.collection("users").document(uid)
        doc = doc_ref.get()

        if not doc.exists:
            logger.error(f"User info not found for UID: {uid}")
            raise HTTPException(status_code=404, detail="User info not found.")

        user_data = doc.to_dict()
        logger.info(f"Retrieved user data: {user_data}")

        return {
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name")
        }
    
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "XOM"
]

@router.get("/user/watchlist")
async def get_user_watchlist(user=Depends(verify_token)):
    try:
        # Get the user ID from the token
        uid = user["localId"]

        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists or "watchlist" not in user_doc.to_dict():
            user_ref.set({"watchlist": DEFAULT_WATCHLIST}, merge=True)
            watchlist = DEFAULT_WATCHLIST
        else:
            watchlist = user_doc.to_dict().get("watchlist", [])

        stocks_collection = db.collection("Stocks")
        stock_docs = [stocks_collection.document(t).get() for t in watchlist]
        stock_data = [doc.to_dict() | {"ticker": doc.id} for doc in stock_docs if doc.exists]

        # Fetch daily performance for the watchlist
        stock_tickers = [doc["ticker"] for doc in stock_data]
        performance = get_daily_performance(stock_tickers)

        result = {"user_id": uid, "watchlist": stock_data}

        for stock in result["watchlist"]:
            ticker = stock["ticker"]
            if ticker in performance:
                stock["daily_performance"] = performance[ticker]
            else:
                stock["daily_performance"] = None
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving watchlist: {str(e)}")

@router.get("/stocks")
async def get_all_stocks():
    try:
        stocks = db.collection("Stocks").stream()
        stock_list = [doc.to_dict() | {"ticker": doc.id} for doc in stocks]
        return {"stocks": stock_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")

@router.post("/user/watchlist/add")
async def add_to_watchlist(ticker: str, user=Depends(verify_token)):
    try:
        uid = user["localId"]
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        watchlist = user_doc.to_dict().get("watchlist", []) if user_doc.exists else []

        if ticker not in watchlist:
            watchlist.append(ticker)
            user_ref.update({"watchlist": watchlist})

        return {"message": f"{ticker} added to watchlist.", "watchlist": watchlist}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add stock: {str(e)}")

@router.post("/user/watchlist/remove")
async def remove_from_watchlist(ticker: str, user=Depends(verify_token)):
    try:
        uid = user["localId"]
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        watchlist = user_doc.to_dict().get("watchlist", []) if user_doc.exists else []

        if ticker in watchlist:
            watchlist.remove(ticker)
            user_ref.update({"watchlist": watchlist})

        return {"message": f"{ticker} removed from watchlist.", "watchlist": watchlist}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to remove stock: {str(e)}")
