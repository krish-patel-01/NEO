"""Util that calls WolframAlpha."""
"""A wrapper around Wolfram Alpha. Useful for when you need to answer questions about Math, Science, Technology, Geography, Culture, Society and Everyday Life. Input should be a search query."""

import wolframalpha
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["WOLFRAM_ALPHA_APPID"] = os.getenv("WOLFRAM_ALPHA_APPID")

client = wolframalpha.Client(os.environ.get("WOLFRAM_ALPHA_APPID"))

def WolframAlphaAPIWrapper_run(query: str) -> str:
    """Run query through WolframAlpha and parse result."""
    res = client.query(query)
    
    try:
        assumption = next(res.pods).text
        answer = next(res.results).text
    except StopIteration:
        return "Wolfram Alpha wasn't able to answer it"

    if answer is None or answer == "":
        # We don't want to return the assumption alone if answer is empty
        return "No good Wolfram Alpha Result was found"
    else:
        return f"{assumption} --> {answer}"
    

if __name__ == "__main__":
    query = "Who is the PM of UK?"
    # query = "6 * 8"
    print(WolframAlphaAPIWrapper_run(query))