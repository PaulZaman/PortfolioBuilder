from fastapi import HTTPException
from app.services.firebase_init import db

async def save_questionnaire_response_firebase(uid: str, answers: list):
    """Save or update a user's questionnaire response in Firebase (no nested arrays).

    Args:
        uid (str): The user's unique identifier.
        answers (list of list of str): User's answers (multi-answer per question).

    Returns:
        dict: The saved response.
    """
    if not uid:
        raise HTTPException(status_code=400, detail="Missing user ID (uid).")

    # Flatten to dict: {"1": [...], "2": [...], ...}
    formatted_answers = {str(i + 1): ans for i, ans in enumerate(answers)}

    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        user_ref.set({"questionnaire_response": formatted_answers})
    else:
        user_ref.update({"questionnaire_response": formatted_answers})

    return {"uid": uid, "questionnaire_response": formatted_answers}

async def get_questionnaire_response_firebase(uid: str):
    """Retrieve a user's questionnaire response from Firebase.

    Args:
        uid (str): The user's unique identifier.

    Returns:
        dict: The user's questionnaire responses (question number -> list of answers).
    """
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_doc.to_dict()
    answers = user_data.get("questionnaire_response")

    if not answers:
        raise HTTPException(status_code=404, detail="No questionnaire response found for this user.")

    return answers

async def save_ai_metric_suggestions(uid: str, result: dict):
    if not uid or not result:
        raise HTTPException(status_code=400, detail="Missing uid or result")

    user_ref = db.collection("users").document(uid)
    user_ref.set({"ai_metric_suggestions": result}, merge=True)
    return {"uid": uid, "ai_metric_suggestions": result}

async def get_ai_metric_suggestions(uid: str):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    data = user_doc.to_dict().get("ai_metric_suggestions")
    if not data:
        raise HTTPException(status_code=404, detail="No metric suggestions found")

    return data

async def save_ai_asset_suggestions(uid: str, result: dict):
    if not uid or not result:
        raise HTTPException(status_code=400, detail="Missing uid or result")

    user_ref = db.collection("users").document(uid)
    user_ref.set({"ai_asset_suggestions": result}, merge=True)
    return {"uid": uid, "ai_asset_suggestions": result}

async def get_ai_asset_suggestions(uid: str):
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    data = user_doc.to_dict().get("ai_asset_suggestions")
    if not data:
        raise HTTPException(status_code=404, detail="No asset suggestions found")

    return data