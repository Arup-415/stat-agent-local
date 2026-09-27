from fastapi import APIRouter, Header

from app.models import QuestionRequest
from app.dataset_store import dataset_store
from app.agent import ask_agent
from app.analyzer import make_json_serializable
from app.memory import session_memory_store

router = APIRouter()


@router.post("/chat")
def chat(request: QuestionRequest, session_id: str = Header(..., alias="X-Session-ID", min_length=16, max_length=128)):
    """
    Chat with the currently uploaded dataset.
    """

    # Get the currently uploaded dataframe
    df = dataset_store.get_dataset(session_id)

    if df is None:
        return {
            "error": "No dataset uploaded. Please upload a CSV first."
        }

    # Ask the statistics AI agent
    result = ask_agent(
        question=request.question,
        df=df,
        conversation_memory=session_memory_store.get(session_id),
    )

    return make_json_serializable(result)