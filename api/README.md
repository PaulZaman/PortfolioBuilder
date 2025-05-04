# 📈 Intelligent Portfolio Optimization Platform - Backend (API)

FastAPI backend for authentication, user profile management, and integration with Firebase services.

---

## 🚀 How to Launch the Backend

### Prerequisites

Make sure you have the following files (not in the repo):

- **api/.env**: Environment variables for the backend.
- **api/app/core/keys/serviceAccountKey.json**: Firebase service account key.

Now, you can navigate to the `api` directory and set up the backend.

```bash
cd api
```

### Create venv and Activate

Make sure you are in the api directory of the project.

```bash
# Create a virtual environment
python -m venv venv
```
Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
uvicorn app.main:app --reload
```


# 📊 API Endpoints

## Authentication

### POST /api/signup
Register a new user and store additional profile data.  
Body:  
{ "email": string, "password": string, "first_name": string, "last_name": string }  
Returns:  
{ "message": "User created successfully", "token": string, "first_name": string, "last_name": string }

### POST /api/login  
Authenticate a user and return a token.  
Body:  
{ "email": string, "password": string }  
Returns:  
{ "message": "Login successful", "token": string }

### GET /api/protected  
Test route to verify if the token is valid.  
Headers: Authorization  
Returns:  
{ "message": "Welcome, <email>! You are authenticated." }

### GET /api/user-info  
Get profile information of the authenticated user.  
Headers: Authorization  
Returns:  
{ "email": string, "first_name": string, "last_name": string }

## Stock and Watchlist Management

### GET /api/stocks  
Retrieve the full list of available stocks.  
Returns:  
{ "stocks": [ { "ticker": string, ... }, ... ] }

### GET /api/user/watchlist  
Get the user's current watchlist with daily performance data.  
Headers: Authorization  
Returns:  
{ "user_id": string, "watchlist": [ { "ticker": string, ..., "daily_performance": float|null }, ... ] }

### POST /api/user/watchlist/add  
Add a stock to the user's watchlist.  
Headers: Authorization | Query: ticker  
Returns:  
{ "message": "<ticker> added to watchlist.", "watchlist": [...] }

### POST /api/user/watchlist/remove  
Remove a stock from the user's watchlist.  
Headers: Authorization | Query: ticker  
Returns:  
{ "message": "<ticker> removed from watchlist.", "watchlist": [...] }

## Portfolio Management

### POST /api/portfolios/create  
Create a new portfolio with tickers, weights, and start date.  
Headers: Authorization  
Body:  
{ "tickers": [...], "weights": [...], "start_date": "YYYY-MM-DD", "name": string (optional) }  
Returns:  
{ "message": "Portfolio created successfully", "portfolio": { ... } }

### GET /api/portfolios/get  
Get all portfolios created by the authenticated user.  
Headers: Authorization  
Returns:  
{ "portfolios": [ { ... }, ... ] }

### GET /api/portfolios/get/{ptfid}  
Retrieve a specific portfolio by its ID.  
Headers: Authorization  
Returns:  
{ "portfolio": { ... } }

### DELETE /api/portfolios/delete/{ptfid}  
Delete a specific portfolio by its ID.  
Headers: Authorization  
Returns:  
{ "message": "Portfolio deleted successfully" }

### POST /api/optimize/{ptfid}
Optimize a portfolio by its ID.
Headers: Authorization
Body:
{ "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "interval": string (optional), "metric": string (optional), "allow_short": boolean (optional) }
Returns: 
{ "portfolio_name": string, "tickers": [...], "optimized_weights": { ticker: weight, ... }, "metric": string, "result": { "weights": { ticker: weight, ... }, "score": float, "cum_returns": { date: value, ... } } }

### POST /api/optimize
Optimize a new sample portfolio.
Headers: Authorization
Body:
{ "tickers": [...], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "interval": string (optional), "metric": string (optional), "allow_short": boolean (optional) }
Returns:
{ "tickers": [...], "optimized_weights": { ticker: weight, ... }, "metric": string, "result": { "weights": { ticker: weight, ... }, "score": float, "cum_returns": { date: value, ... } } }
