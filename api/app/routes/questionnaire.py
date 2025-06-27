from fastapi import APIRouter, HTTPException
from  pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/questionnaires", tags=["Questionnaires"])

# Définir les réponses valides
QUESTIONS = {
    1: [
        "Je veux avant tout préserver mon capital, quitte à avoir un faible rendement.",
        "Je cherche un bon équilibre entre sécurité et performance.",
        "Je suis prêt à accepter des fluctuations pour viser un rendement supérieur.",
        "Je vise un rendement maximum, même avec un risque élevé et de la volatilité."
    ],
    2: [
        "Les technologies, l’innovation et le numérique.",
        "La santé, les biotechs et les sciences de la vie.",
        "L’immobilier, la construction ou les infrastructures.",
        "Les énergies (renouvelables ou traditionnelles)."
    ],
    3: [
        "Je veux un portefeuille diversifié à l’échelle mondiale.",
        "Je préfère me concentrer sur l’Europe.",
        "Je vise surtout l’Amérique du Nord (USA / Canada).",
        "Je suis intéressé par l’Asie et les marchés émergents."
    ],
    4: [
        "Des actions d’entreprises cotées en Bourse.",
        "Des obligations ou produits plus stables.",
        "Des fonds indiciels (ETF) pour diversifier facilement.",
        "Un portefeuille mixte combinant plusieurs types d’actifs."
    ],
    5: [
        "Je souhaite un retour rapide : moins de 2 ans.",
        "Je prévois un placement sur 2 à 5 ans.",
        "Je préfère un horizon long terme : plus de 5 ans.",
        "Je construis un patrimoine sur plus de 10 ans."
    ]
}

class QuestionnaireResponse(BaseModel):
    answers: List[str]

@router.post("/questionnaire")
def submit_questionnaire(response: QuestionnaireResponse):
    if len(response.answers) != 5:
        raise HTTPException(status_code=400, detail="Il faut 5 réponses, une par question.")

    # Vérifier les réponses
    for idx, user_answer in enumerate(response.answers, start=1):
        if user_answer not in QUESTIONS[idx]:
            raise HTTPException(
                status_code=400,
                detail=f"Réponse invalide pour la question {idx} : '{user_answer}'"
            )
    return {"message": "Réponses enregistrées avec succès", "data": response.answers}
