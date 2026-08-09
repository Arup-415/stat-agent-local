from fastapi import APIRouter

from app.models import QuestionRequest
from app.session import get_dataframe
from app.agent import ask_agent
from app.memory import memory


router = APIRouter()


@router.post("/chat")
def chat(request: QuestionRequest):
    """
    Chat with the uploaded dataset.

    The currently uploaded dataset is retrieved from the session.
    Conversation context is maintained through the memory system.
    """

    # --------------------------------------------------
    # Get currently uploaded dataframe
    # --------------------------------------------------

    df = get_dataframe()

    # --------------------------------------------------
    # Check whether a dataset exists
    # --------------------------------------------------

    if df is None:

        return {
            "error": "No dataset uploaded. Please upload a CSV first."
        }

    # --------------------------------------------------
    # Get previous conversation context
    # --------------------------------------------------

    previous_question = memory.get_last_question()
    previous_result = memory.get_last_result()

    # --------------------------------------------------
    # Ask the Statistics AI Agent
    # --------------------------------------------------

    result = ask_agent(
        question=request.question,
        df=df,
        previous_question=previous_question,
        previous_result=previous_result
    )

    # --------------------------------------------------
    # Store the conversation in memory
    # --------------------------------------------------

    memory.update(
        question=request.question,
        result=result,
        dataframe=df
    )

    # --------------------------------------------------
    # Return response
    # --------------------------------------------------

    return result