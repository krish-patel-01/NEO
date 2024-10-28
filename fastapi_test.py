# import os
# from enum import Enum
# from typing import List, Dict
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from groq import Groq
# from agent import agent_loop

# class Agent(Enum):
#     KEVIN = "kevin"
#     STUART = "stuart"
#     BOB = "bob"

# class ChatMessage(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     message: str
#     agent: Agent

# class ChatResponse(BaseModel):
#     message: str
#     agent: Agent

# class ChatApplication:
#     def __init__(self):
#         self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
#         self.chat_history: List[Dict[str, str]] = []

#     def process_kevin_input(self, user_input: str) -> str:
#         self.chat_history.append({"role": "user", "content": user_input})
#         response = self.client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=self.chat_history,
#             temperature=1.2
#         )
#         assistant_message = response.choices[0].message.content
#         self.chat_history.append({"role": "assistant", "content": assistant_message})
#         return assistant_message

#     def process_stuart_input(self, user_input: str) -> str:
#         stuart_result = agent_loop(query=user_input, verbose=False)
#         self.chat_history.append({"role": "user", "content": user_input})
#         self.chat_history.append({"role": "assistant", "content": stuart_result})
#         return stuart_result

#     def process_bob_input(self, user_input: str) -> str:
#         return "BOB!!!"

# app = FastAPI()
# chat_app = ChatApplication()

# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     if request.agent == Agent.KEVIN:
#         response = chat_app.process_kevin_input(request.message)
#     elif request.agent == Agent.STUART:
#         response = chat_app.process_stuart_input(request.message)
#     elif request.agent == Agent.BOB:
#         response = chat_app.process_bob_input(request.message)
#     else:
#         raise HTTPException(status_code=400, detail="Invalid agent")
    
#     return ChatResponse(message=response, agent=request.agent)

# @app.get("/chat_history", response_model=List[ChatMessage])
# async def get_chat_history():
#     return [ChatMessage(**msg) for msg in chat_app.chat_history]

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=6000)


from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Dict
import os
from groq import Groq
from agent import agent_loop

class Agent(str, Enum):
    KEVIN = "kevin"
    STUART = "stuart"
    BOB = "bob"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    agent: Agent

class ChatResponse(BaseModel):
    message: str
    agent: Agent

class ChatApplication:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.chat_history: List[Dict[str, str]] = []

    def process_kevin_input(self, user_input: str) -> str:
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=self.chat_history,
            temperature=1.2
        )
        assistant_message = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message

    def process_stuart_input(self, user_input: str) -> str:
        stuart_result = agent_loop(query=user_input, verbose=False)
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": stuart_result})
        return stuart_result

    def process_bob_input(self, user_input: str) -> str:
        return "BOB!!!"

app = FastAPI()
chat_app = ChatApplication()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if request.agent == Agent.KEVIN:
        response = chat_app.process_kevin_input(request.message)
    elif request.agent == Agent.STUART:
        response = chat_app.process_stuart_input(request.message)
    elif request.agent == Agent.BOB:
        response = chat_app.process_bob_input(request.message)
    else:
        raise HTTPException(status_code=400, detail="Invalid agent")
    
    return ChatResponse(message=response, agent=request.agent)

@app.get("/chat_history", response_model=List[ChatMessage])
async def get_chat_history():
    return [ChatMessage(**msg) for msg in chat_app.chat_history]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)