from fastapi import HTTPException
from app.core.firebase_init import db


DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "XOM"
]

async def get_all_stocks_firebase():
	"""Get all stocks from Firebase Firestore.

	Returns:
		list: A list of dictionaries containing stock data.
		format of the dictionary is the same as the one in the Firestore collection.
	"""
	stocks = db.collection("Stocks").stream()
	stock_list = [doc.to_dict() | {"ticker": doc.id} for doc in stocks]
	return stock_list

async def get_user_watchlist_firebase(uid:str):
	"""Get the user's watchlist from Firebase Firestore.
	Fetches the user's watchlist from Firestore. If the watchlist does not exist, it initializes it with a default list of stocks.


	Args:
		uid (str): The user's unique identifier.

	Returns:
		list: A list of dictionaries containing stock data in the user's watchlist.
	"""
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

	return stock_data

async def add_to_watchlist_firebase(ticker: str, uid: str):
	"""Add a stock to the user's watchlist in Firebase Firestore.
	this checks to make sure the stock is in the database before adding it to the watchlist.

	Args:
		ticker (str): The stock ticker symbol to add.
		uid (str): The user's unique identifier.

	Returns:
		list: The updated watchlist after adding the stock.
	"""
	user_ref = db.collection("users").document(uid)
	user_doc = user_ref.get()
	watchlist = user_doc.to_dict().get("watchlist", []) if user_doc.exists else []

	# Check if the ticker exists in the Stocks collection
	stocks = await get_all_stocks_firebase()
	if ticker not in [stock["ticker"] for stock in stocks]:
		raise HTTPException(status_code=400, detail=f"{ticker} is not a valid stock ticker. It was not found in the database.")

	# If the ticker is not already in the watchlist, add it
	if ticker not in watchlist:
		watchlist.append(ticker)
		user_ref.update({"watchlist": watchlist})
	else:
		raise HTTPException(status_code=400, detail=f"{ticker} is already in the watchlist.")

	return watchlist

async def remove_from_watchlist_firebase(ticker: str, uid: str):
	"""Remove a stock from the user's watchlist in Firebase Firestore.

	Args:
		ticker (str): The stock ticker symbol to remove.
		uid (str): The user's unique identifier.

	Returns:
		list: The updated watchlist after removing the stock.
	"""
	# Fetch the user's watchlist
	user_ref = db.collection("users").document(uid)
	user_doc = user_ref.get()

	# Check if the user document exists and get the watchlist
	if not user_doc.exists:
		raise HTTPException(status_code=404, detail="User not found.")
	
	# Get the watchlist from the user document
	watchlist = user_doc.to_dict().get("watchlist", []) 

	if ticker in watchlist:
		watchlist.remove(ticker)
		user_ref.update({"watchlist": watchlist})
	else:
		raise HTTPException(status_code=400, detail=f"{ticker} is not in the watchlist.")

	return watchlist
