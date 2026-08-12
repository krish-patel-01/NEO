"""HTTP API over the NEO chat application.

    uvicorn neo.api:app --port 9000
    # or: python -m neo.api

Requires the optional API extra:  pip install -e ".[api]"
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from neo.chat import ChatApplication

app = FastAPI(title="NEO Chatbot API")

# Built on first request rather than at import. Constructing ChatApplication
# creates a Groq client, so doing it at module scope would make importing this
# module fail whenever GROQ_API_KEY is absent — including in CI.
_chatbot: ChatApplication | None = None


def get_chatbot() -> ChatApplication:
    global _chatbot
    if _chatbot is None:
        _chatbot = ChatApplication()
    return _chatbot


class Message(BaseModel):
    content: str
    think_mode: bool = False


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(message: Message) -> ChatResponse:
    try:
        chatbot = get_chatbot()
        user_input = f"@think {message.content}" if message.think_mode else message.content

        chatbot.process_input(user_input)

        return ChatResponse(response=chatbot.chat_history[-1]["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/history")
async def get_history() -> dict:
    return {"history": get_chatbot().chat_history}


@app.delete("/clear_chat")
async def clear_history() -> dict:
    get_chatbot().chat_history.clear()
    return {"message": "Chat history cleared"}


def main() -> None:
    # Bound to localhost by default. There is no authentication on these routes
    # and history is shared by every caller, so exposing this on 0.0.0.0 hands
    # anyone who can reach the port both your Groq quota and the conversation.
    import os

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("NEO_API_HOST", "127.0.0.1"),
        port=int(os.getenv("NEO_API_PORT", "9000")),
    )


if __name__ == "__main__":
    main()
