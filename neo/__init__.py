"""NEO — a ReAct agent with web search and Wolfram Alpha, running on Groq."""

from dotenv import load_dotenv

# Loaded once, here, so every entry point (chat, examples, direct imports) picks
# up .env without each module calling load_dotenv() itself.
load_dotenv()

__version__ = "0.1.0"
