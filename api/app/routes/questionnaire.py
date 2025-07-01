from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List
import json
import os
from app.services.firebase_watchlist import get_all_stocks_firebase
from app.services.firebase_auth import verify_token
from app.services.firebase_questionnaire import save_questionnaire_response_firebase, get_questionnaire_response_firebase
from app.services.firebase_questionnaire import (
    save_ai_asset_suggestions,
    save_ai_metric_suggestions,
    get_ai_asset_suggestions,
    get_ai_metric_suggestions
)
from app.services.openai_questionnaire_suggestions import getTickerSuggestions, getRecommendedMetrics

router = APIRouter(prefix="/api/questionnaires", tags=["Questionnaires"])

# Charger les questions depuis le fichier JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "..", "services", "questionnaire.json")

with open(file_path, "r") as f:
    QUESTIONS = json.load(f)

# Route 1: GET questionnaire
@router.get("/")
def get_questionnaire():
    return QUESTIONS

@router.post("/")
async def submit_questionnaire(
    request: Request,
    user=Depends(verify_token)
):
    uid = user["localId"]
    data = await request.json()
    answers: List[List[str]] = data.get("answers", [])

    if len(answers) != len(QUESTIONS):
        raise HTTPException(status_code=400, detail=f"Il faut {len(QUESTIONS)} ensembles de réponses.")

    for idx, answer_list in enumerate(answers, start=1):
        q = QUESTIONS.get(str(idx)) or QUESTIONS.get(idx)
        if not q:
            raise HTTPException(status_code=400, detail=f"Question {idx} introuvable.")
        valid_answers = q["answers"]
        for ans in answer_list:
            if ans not in valid_answers:
                raise HTTPException(status_code=400, detail=f"Réponse invalide pour la question {idx} : '{ans}'")

    await save_questionnaire_response_firebase(uid, answers)

    return {"message": "Réponses enregistrées avec succès", "data": answers}

@router.get("/generate-stock-suggestions")
async def generate_stock_suggestions(user=Depends(verify_token)):
    uid = user["localId"]

    answers = await get_questionnaire_response_firebase(uid)
    if not answers:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée pour l'utilisateur.")
    
    stocks_firebase = await get_all_stocks_firebase()
    result = getTickerSuggestions(stocks_firebase, answers)

    await save_ai_asset_suggestions(uid, {"result": result})

    return {"result": result}

@router.get("/generate-metric-suggestions")
async def generate_metric_suggestions(user=Depends(verify_token)):
    uid = user["localId"]

    answers = await get_questionnaire_response_firebase(uid)
    if not answers:
        raise HTTPException(status_code=404, detail="Aucune réponse trouvée pour l'utilisateur.")

    result = getRecommendedMetrics(answers)

    await save_ai_metric_suggestions(uid, {"result": result})

    return {"result": result}

@router.get("/stock-suggestions")
async def get_stock_suggestions(user=Depends(verify_token)):
    uid = user["localId"]
    return await get_ai_asset_suggestions(uid)

@router.get("/metric-suggestions")
async def get_metric_suggestions(user=Depends(verify_token)):
    uid = user["localId"]
    return await get_ai_metric_suggestions(uid)

@router.get("/response")
async def get_user_questionnaire_response(user=Depends(verify_token)):
    uid = user["localId"]

    answers = await get_questionnaire_response_firebase(uid)

    return {"uid": uid, "questionnaire_response": answers}

