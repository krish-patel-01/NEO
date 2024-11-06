import os
from typing import List, Dict
from groq import Groq
from agent import agent_loop

class ChatApplication:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.chat_history: List[Dict[str, str]] = []

    def run(self):
        while True:
            user_input = input(">>> ")
            if user_input.lower() == "@bye":
                break
            if not user_input:
                for _ in range(3):
                    print("Please provide some input...")
                    user_input = input(">>> ")
                    if user_input:
                        break
            self.process_input(user_input)

    def process_input(self, user_input: str):
        if "@think" in user_input.lower():
            # Remove @think and process using agent system
            cleaned_input = user_input.replace("@think", "").strip()
            response = agent_loop(query=cleaned_input, verbose=True, history=self.chat_history)
        else:
            # Process normally using LLM
            self.chat_history.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=self.chat_history,
                max_tokens=1500,
                temperature=1.2
            )
            response = response.choices[0].message.content
            
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": response})
        print("NEO:", response)

if __name__ == "__main__":
    ChatApplication().run()