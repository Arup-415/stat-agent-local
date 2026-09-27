import ollama

MODEL_NAME = "qwen2.5:7b"   # Change this if you installed another model


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the local Ollama model.
    """

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        return response["message"]["content"]
    except Exception as error:
        return f"The statistical result is available, but the local AI model could not respond ({error})."