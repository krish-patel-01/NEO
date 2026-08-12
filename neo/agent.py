"""ReAct-style agent loop backed by Groq."""

import os
import re
import time

from groq import Groq

from neo.console import print_text
from neo.prompts import system_prompt
from neo.tools import general_search, wolfram_alpha

# Model is configurable — Groq retires model IDs regularly, and a hardcoded one
# turns into a 404 at runtime months later.
DEFAULT_MODEL = os.getenv("NEO_MODEL", "llama-3.3-70b-versatile")

# Tool dispatch table. Previously the loop did `eval(f'{chosen_tool}("""{arg}""")')`
# on text produced by the model, which let any model output containing a quote
# sequence execute arbitrary Python. A dict lookup can only ever call these two.
TOOLS = {
    "general_search": general_search,
    "wolfram_alpha": wolfram_alpha,
}


def _make_client() -> Groq:
    """Build a Groq client, failing with a clear message if the key is absent."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key, "
            "or export GROQ_API_KEY in the environment."
        )
    return Groq(api_key=api_key)


class Agent:
    def __init__(
        self,
        client: Groq,
        system: str = "",
        history: list | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.client = client
        self.system = system
        self.model = model
        self.messages: list[dict[str, str]] = []
        self.max_tokens = 5000  # Safe limit below the 6000 TPM
        if self.system:
            self.messages.append({"role": "system", "content": system})
        if history:
            self.messages.extend(history)

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        # Rough estimation: ~6 chars per token
        return len(text) // 6

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
                if not self.messages:
                    raise ValueError("No messages to process")

                total_tokens = sum(
                    self.estimate_tokens(m.get("content", "")) for m in self.messages
                )

                if total_tokens > self.max_tokens:
                    self.truncate_history()

                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    max_tokens=1500,
                    temperature=0.7,
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


def agent_loop(
    query: str = "",
    max_iterations: int = 20,
    verbose: bool = True,
    history: list | None = None,
    client: Groq | None = None,
):
    """Run the ReAct loop until the model emits an Answer or iterations run out."""
    client = client or _make_client()
    agent = Agent(client=client, system=system_prompt, history=history)

    next_prompt = query
    for _ in range(max_iterations):
        result = agent(next_prompt)

        if verbose:
            print_text(result, "o")

        if "Answer" in result:
            return result.split("Answer:")[1].strip()

        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)

            if action:
                chosen_tool, arg = action[0][0], action[0][1]
                tool_fn = TOOLS.get(chosen_tool)
                if tool_fn is not None:
                    try:
                        next_prompt = f"Observation: {tool_fn(arg)}"
                    except Exception as e:
                        next_prompt = f"Observation: Tool '{chosen_tool}' failed: {e}"
                else:
                    next_prompt = "Observation: Tool not found"
            else:
                next_prompt = "Observation: Action format not recognized"

            if verbose:
                print_text(next_prompt + "\n", "g")

    return "Error: reached the iteration limit without producing an answer."
