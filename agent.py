import os
import re
import time
from groq import Groq
from print_text import print_text
from tools import general_search, wolfram_alpha
from agent_prompt import system_prompt
from dotenv import load_dotenv

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Agent:
    def __init__(self, client: Groq, system: str = "", history: list = None) -> None:
        self.client = client
        self.system = system
        self.messages = []
        self.max_tokens = 5000  # Safe limit below the 6000 TPM
        if self.system:
            self.messages.append({"role": "system", "content": system})
        if history:
            self.messages.extend(history)

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        try:
            # Rough estimation: ~6 chars per token
            return len(text) // 6
        except Exception:
            return 0

    def truncate_history(self):
        if len(self.messages) > 5:
            if self.messages[0]["role"] == "system":
                # Keep system prompt and remove first two exchanges (4 messages)
                system = self.messages[0]
                self.messages = self.messages[5:]  # Skip system + first 2 exchanges
                self.messages.insert(0, system)
            else:
                # No system prompt, just remove first two exchanges (4 messages)
                self.messages = self.messages[4:]

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        retries = 2
        while retries >= 0:
            try:
                # Skip token estimation if no messages
                if not self.messages:
                    raise ValueError("No messages to process")
                    
                total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in self.messages)
                
                if total_tokens > self.max_tokens:
                    self.truncate_history()
                
                completion = client.chat.completions.create(
                    model="llama-3.1-70b-versatile", 
                    messages=self.messages, 
                    max_tokens=1500, 
                    temperature=0.7
                )
                return completion.choices[0].message.content
            except Exception as e:
                if "rate_limit_exceeded" in str(e) and retries > 0:
                    self.truncate_history()
                    retries -= 1
                    continue
                print(f"Error: {e}")
                time.sleep(5)
                retries -= 1
        return "Error: Unable to get response after retries"

def agent_loop(query: str = "", max_iterations=20, verbose=True, history: list = None):
    agent = Agent(client=client, system=system_prompt, history=history)

    tools = ["general_search", "wolfram_alpha"]

    next_prompt = query
    i = 0
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        
        if verbose: print_text(result, "o")
        
        if "Answer" in result and "Observation" in result and "Action" in result:
            observation = re.search(r"Observation:(.*?)Answer:", result, re.DOTALL).group(1).strip()
            answer = re.search(r"Answer:(.*)", result, re.DOTALL).group(1).strip()
            
            if observation > answer:
                return f"{observation}\n\n{answer}"
            else:
                pass
        
        if "Answer" in result:
            final_answer = result.split("Answer:")[1].strip()
            return final_answer

        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
            
            if action:
                chosen_tool = action[0][0]
                arg = action[0][1]

                if chosen_tool in tools:
                    result_tool = eval(f'{chosen_tool}("""{arg}""")')
                    next_prompt = f"Observation: {result_tool}"

                else:
                    next_prompt = "Observation: Tool not found"
            else:
                next_prompt = "Observation: Action format not recognized"
                
            
            if verbose: print_text(next_prompt+"\n", "g")

