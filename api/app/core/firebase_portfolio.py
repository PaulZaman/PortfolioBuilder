from fastapi import HTTPException
from app.core.firebase_init import db

async def create_new_portfolio_firebase(uid: str, ptfid:str, tickers: list, weights: list, dates: list, performance: list, portfolio_name: str = "New Portfolio"):
	"""Create a new portfolio in Firebase Firestore.

	Args:
		uid (str): The user's unique identifier.
		ptfid (str): The portfolio's unique identifier.
		tickers (list): _list of stock tickers in the portfolio_
		weights (list): _list of weights for each stock in the portfolio_
		dates (list): list of the dates for the portfolio
		performance (list): list of the daily performance for the portfolio
	"""
	# Before, we check if the portfolio does not already exist
	# Get the user portfolios
	user_ptfs = await get_user_portfolios_firebase(uid)
	if user_ptfs:
		for ptf in user_ptfs:
			if portfolio_name == ptf["name"]:
				raise HTTPException(status_code=400, detail="Portfolio with this name already exists")
			if tickers == ptf["tickers"] and weights == ptf["weights"] and dates == ptf["dates"]:
				raise HTTPException(status_code=400, detail="Portfolio with this configuration already exists")
	# Create a new portfolio document
	portfolio_data = {
		"uid": uid,
		"ptfid": ptfid,
		"tickers": tickers,
		"weights": weights,
		"dates": dates,
		"performance": performance,
		"name": portfolio_name
	}
	# Save to 'portfolios' collection
	db.collection("portfolios").document(ptfid).set(portfolio_data)

	# Link portfolio to the user
	user_ref = db.collection("users").document(uid)
	user_doc = user_ref.get()

	if not user_doc.exists:
		raise HTTPException(status_code=404, detail="User not found")

	user_data = user_doc.to_dict()
	existing_portfolios = user_data.get("portfolios", [])
	existing_portfolios.append(ptfid)
	user_ref.update({"portfolios": existing_portfolios})

	return portfolio_data

async def get_user_portfolios_firebase(uid: str):
	# Get user document
	user_ref = db.collection("users").document(uid)
	user_doc = user_ref.get()

	if not user_doc.exists:
		raise HTTPException(status_code=404, detail="User not found")

	user_data = user_doc.to_dict()
	portfolio_ids = user_data.get("portfolios", [])

	# Fetch each portfolio by ID
	portfolios = []
	for ptf_id in portfolio_ids:
		ptf_doc = db.collection("portfolios").document(ptf_id).get()
		if ptf_doc.exists:
			ptf_data = ptf_doc.to_dict()
			ptf_data["portfolio_id"] = ptf_id
			portfolios.append(ptf_data)

	return portfolios

async def get_portfolio_firebase(ptfid: str):
	"""Get a portfolio from Firebase Firestore.

	Args:
		ptfid (str): The portfolio's unique identifier.

	Returns:
		dict: The portfolio data.
	"""
	ptf_ref = db.collection("portfolios").document(ptfid)
	ptf_doc = ptf_ref.get()

	if not ptf_doc.exists:
		raise HTTPException(status_code=404, detail="Portfolio not found")

	return ptf_doc.to_dict()

async def delete_portfolio_firebase(uid: str, ptfid: str):
	"""Delete a portfolio from Firebase Firestore.

	Args:
		uid (str): The user's unique identifier.
		ptfid (str): The portfolio's unique identifier.
	"""
	# Get the user document
	user_ref = db.collection("users").document(uid)
	user_doc = user_ref.get()

	if not user_doc.exists:
		raise HTTPException(status_code=404, detail="User not found")

	user_data = user_doc.to_dict()
	existing_portfolios = user_data.get("portfolios", [])

	if ptfid not in existing_portfolios:
		raise HTTPException(status_code=404, detail="Portfolio not found")

	# Delete the portfolio document
	db.collection("portfolios").document(ptfid).delete()

	# Remove the portfolio ID from the user's list of portfolios
	existing_portfolios.remove(ptfid)
	user_ref.update({"portfolios": existing_portfolios})
