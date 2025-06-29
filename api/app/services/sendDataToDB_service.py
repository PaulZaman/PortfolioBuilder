import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY        = os.getenv('FIREBASE_API_KEY')
PROJECT_ID     = os.getenv('FIREBASE_PROJECT_ID')
collection     = 'Stocks'

# The base URL for the Firestore REST API
BASE_URL = (
    f"https://firestore.googleapis.com/v1/"
    f"projects/{PROJECT_ID}/databases/(default)/documents/{collection}"
)

# List of stocks to add
stocks = [
    # ESG ETFs
    {'ticker': 'ESGU', 'name': 'iShares ESG Aware MSCI USA ETF', 'sector': 'ESG'},
    {'ticker': 'SUSA', 'name': 'iShares MSCI USA ESG Select ETF', 'sector': 'ESG'},
    {'ticker': 'VFTAX', 'name': 'Vanguard FTSE Social Index Fund Admiral Shares', 'sector': 'ESG'},
    {'ticker': 'DSI', 'name': 'iShares MSCI KLD 400 Social ETF', 'sector': 'ESG'},
    {'ticker': 'CRBN', 'name': 'iShares MSCI ACWI Low Carbon Target ETF', 'sector': 'ESG'},
    {'ticker': 'SPYG', 'name': 'SPDR S&P 500 Growth ETF (incl. ESG-friendly firms)', 'sector': 'ESG / Growth'},

    {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'sector': 'Stable / Total Market'},
    {'ticker': 'SCHD', 'name': 'Schwab U.S. Dividend Equity ETF', 'sector': 'Stable / Dividends'},
    {'ticker': 'DGRO', 'name': 'iShares Core Dividend Growth ETF', 'sector': 'Stable / Dividends'},
    {'ticker': 'USMV', 'name': 'iShares MSCI USA Min Vol Factor ETF', 'sector': 'Stable / Low Volatility'},
    {'ticker': 'SPLV', 'name': 'Invesco S&P 500 Low Volatility ETF', 'sector': 'Stable / Low Volatility'},
    {'ticker': 'VV', 'name': 'Vanguard Large-Cap ETF', 'sector': 'Stable / Large Cap'},

    # Bond ETFs
    {'ticker': 'TLT', 'name': 'iShares 20+ Year Treasury Bond ETF', 'sector': 'Bonds / Long-Term Treasuries'},
    {'ticker': 'IEF', 'name': 'iShares 7-10 Year Treasury Bond ETF', 'sector': 'Bonds / Intermediate Treasuries'},
    {'ticker': 'SHY', 'name': 'iShares 1-3 Year Treasury Bond ETF', 'sector': 'Bonds / Short-Term Treasuries'},
    {'ticker': 'AGG', 'name': 'iShares Core U.S. Aggregate Bond ETF', 'sector': 'Bonds / Aggregate'},
    {'ticker': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'sector': 'Bonds / Total Market'},
    {'ticker': 'TIP', 'name': 'iShares TIPS Bond ETF', 'sector': 'Bonds / Inflation-Protected'},
]

# Iterate over the stocks and add them to Firestore
for stock in stocks:
    payload = {
        "fields": {
            "ticker": {"stringValue": stock['ticker']},
            "name":   {"stringValue": stock['name']},
            "sector": {"stringValue": stock['sector']}
        }
    }

    url = f"{BASE_URL}?key={API_KEY}&documentId={stock['ticker']}"
    res = requests.post(url, json=payload)

    if res.status_code == 200:
        print(f"{stock['ticker']} added (ID: {stock['ticker']})")
    else:
        print(f"Error ({res.status_code}) for {stock['ticker']}: {res.text}")
