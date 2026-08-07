from fastapi import APIRouter
from app.models import QuestionRequest

router = APIRouter()


@router.post("/chat")
def chat(request: QuestionRequest):

    return {
        "message": "Chat endpoint working!",
        "question": request.question
    }