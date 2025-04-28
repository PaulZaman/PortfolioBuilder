import pyrebase
from fastapi import HTTPException, Header
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env', 'ATT47711.env')
logger.info(f"Loading environment variables from: {env_path}")

if not os.path.exists(env_path):
    logger.error(f"Environment file not found at: {env_path}")
    raise FileNotFoundError(f"Environment file not found at: {env_path}")

load_dotenv(env_path)

# Check required environment variables
required_env_vars = [
    "FIREBASE_API_KEY",
    "FIREBASE_AUTH_DOMAIN",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_STORAGE_BUCKET",
    "FIREBASE_MESSAGING_SENDER_ID",
    "FIREBASE_APP_ID",
    "FIREBASE_DATABASE_URL"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing environment variables: {missing_vars}")
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Print loaded environment variables (excluding sensitive information)
logger.info("Environment variables loaded successfully")
logger.info(f"Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
logger.info(f"Auth Domain: {os.getenv('FIREBASE_AUTH_DOMAIN')}")

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
}

# Initialize Firestore connection
try:
    service_account_path = os.path.join(os.path.dirname(__file__), "keys", "serviceAccountKey.json")
    if not os.path.exists(service_account_path):
        raise FileNotFoundError(f"Service account key file not found at: {service_account_path}")
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firestore initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Firestore: {str(e)}")
    raise

# Initialize Firebase Auth
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
    logger.info("Firebase Auth initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Firebase Auth: {str(e)}")
    raise

def signup_user(email: str, password: str):
    try:
        logger.info(f"Attempting to create user with email: {email}")
        user = auth.create_user_with_email_and_password(email, password)
        logger.info("User created successfully")
        return user
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error during signup: {error_message}")
        if "EMAIL_EXISTS" in error_message:
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "WEAK_PASSWORD" in error_message:
            raise HTTPException(status_code=400, detail="Password is too weak")
        else:
            raise HTTPException(status_code=400, detail=f"Registration failed: {error_message}")

def login_user(email: str, password: str):
    try:
        logger.info(f"Attempting to login user with email: {email}")
        user = auth.sign_in_with_email_and_password(email, password)
        logger.info("Login successful")
        return user
    except Exception as e:
        error_message = str(e)
        logger.error(f"Login error: {error_message}")
        if "INVALID_PASSWORD" in error_message:
            raise HTTPException(status_code=400, detail="Invalid password")
        elif "EMAIL_NOT_FOUND" in error_message:
            raise HTTPException(status_code=400, detail="Email not found")
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")

async def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        user_info = auth.get_account_info(token)
        return user_info['users'][0]
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
