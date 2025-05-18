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
    {'ticker': 'XOM', 'name': 'Exxon Mobil Corporation', 'sector': 'Energy'},
    {'ticker': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
    {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
    {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Communication Services'},
    {'ticker': 'AMZN', 'name': 'Amazon.com, Inc.', 'sector': 'Consumer Discretionary'},
    {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'sector': 'Consumer Discretionary'},
    {'ticker': 'JNJ',  'name': 'Johnson & Johnson', 'sector': 'Health Care'},
    {'ticker': 'PG',   'name': "Procter & Gamble Co.",  'sector': "Consumer Staples"},
    {'ticker': 'VZ',   'name': "Verizon Communications Inc.",  'sector': "Communication Services"},
    {'ticker': 'WMT',  'name': "Walmart Inc.",  'sector': "Consumer Staples"},
    {'ticker': 'TEVA', 'name': 'Teva Pharmaceutical Industries Limited', 'sector': 'Health Care'},

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
