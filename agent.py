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
    def __init__(self, client: Groq, system: str = "") -> None:
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        while True:
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192", messages=self.messages
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)
    

def agent_loop(query: str = "", max_iterations=20, verbose=True):
    agent = Agent(client=client, system=system_prompt)

    tools = ["general_search", "wolfram_alpha"]

    next_prompt = query
    i = 0
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        
        if verbose: print_text(result, "o")
        
        if "Answer" in result:
            # print(result)
            # print(result.split("Answer:")[1].strip())
            # break
            return result.split("Answer:")[1].strip()

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

