from fastapi import APIRouter, Depends
from app.models.user import UserSignup, UserLogin
from app.core.firebase import signup_user, login_user, verify_token
from app.core.firebase import signup_user, db
from app.core.firebase import login_user, verify_token
from fastapi import HTTPException
import logging

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
