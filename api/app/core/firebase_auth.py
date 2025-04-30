from fastapi import HTTPException, Header
from app.core.firebase_init import logger, auth



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

