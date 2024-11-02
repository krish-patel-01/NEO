import os
from enum import Enum
from typing import List, Dict
from groq import Groq
from agent import agent_loop

class Agent(Enum):
    KEVIN = "kevin"
    STUART = "stuart"
    BOB = "bob"

class ChatApplication:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.chat_history: List[Dict[str, str]] = []
        self.current_agent: Agent = Agent.KEVIN

    def run(self):
        while True:
            user_input = self.get_user_input()
            if self.should_switch_agent(user_input):
                self.switch_agent(user_input)
            else:
                self.process_input(user_input)

    def get_user_input(self) -> str:
        prefix = f">>{self.current_agent.value[0].upper()}>> " if self.current_agent != Agent.BOB else ">>> "
        return input(prefix)

    def should_switch_agent(self, user_input: str) -> bool:
        return any(f"@{agent.value}" in user_input.lower() for agent in Agent if agent != self.current_agent)

    def switch_agent(self, user_input: str):
        print("BANANA!!!!")
        lower_input = user_input.lower()
        if "@stuart" in lower_input:
            self.current_agent = Agent.STUART
        elif "@kevin" in lower_input:
            self.current_agent = Agent.KEVIN
        elif "@bob" in lower_input:
            self.current_agent = Agent.BOB

    def process_input(self, user_input: str):
        cleaned_input = self.remove_agent_mentions(user_input)
        
        if self.current_agent == Agent.KEVIN:
            self.process_kevin_input(cleaned_input)
        elif self.current_agent == Agent.STUART:
            self.process_stuart_input(cleaned_input)
        else:
            print("BOB!!!")

    def remove_agent_mentions(self, user_input: str) -> str:
        for agent in Agent:
            user_input = user_input.replace(f"@{agent.value}", "").strip()
        return user_input

    def process_kevin_input(self, user_input: str):
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=self.chat_history,
            max_tokens=1500,
            temperature=1.2
        )
        assistant_message = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": assistant_message})
        print(f"{Agent.KEVIN.value.capitalize()}:", assistant_message)

    def process_stuart_input(self, user_input: str):
        stuart_result = agent_loop(query=user_input, verbose=True, history=self.chat_history)
        print(f"{Agent.STUART.value.capitalize()}:", stuart_result)
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": stuart_result})

if __name__ == "__main__":
    ChatApplication().run()