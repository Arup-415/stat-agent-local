from fastapi import APIRouter

from app.models import QuestionRequest
from app.dataset_store import dataset_store
from app.agent import ask_agent

router = APIRouter()


@router.post("/chat")
def chat(request: QuestionRequest):
    """
    Chat with the currently uploaded dataset.
    """

    # Get the currently uploaded dataframe
    df = dataset_store.get_dataset()

    if df is None:
        return {
            "error": "No dataset uploaded. Please upload a CSV first."
        }

    # Ask the statistics AI agent
    result = ask_agent(
        question=request.question,
        df=df
    )

    return result