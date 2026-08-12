"""Wrapper around Wolfram Alpha.

Answers questions about maths, science, technology, geography, culture, society
and everyday life. Input should be a search query.
"""

import os

import wolframalpha

_client = None


def _get_client() -> wolframalpha.Client:
    """Build the client lazily.

    Previously this module did `os.environ["WOLFRAM_ALPHA_APPID"] = os.getenv(...)`
    at import time, which raises TypeError on import when the variable is unset —
    so a missing key broke the whole program rather than just this tool.
    """
    global _client
    if _client is None:
        app_id = os.getenv("WOLFRAM_ALPHA_APPID")
        if not app_id:
            raise RuntimeError(
                "WOLFRAM_ALPHA_APPID is not set. Add it to .env or the environment."
            )
        _client = wolframalpha.Client(app_id)
    return _client


def WolframAlphaAPIWrapper_run(query: str) -> str:
    """Run query through WolframAlpha and parse result."""
    res = _get_client().query(query)

    try:
        assumption = next(res.pods).text
        answer = next(res.results).text
    except StopIteration:
        return "Wolfram Alpha wasn't able to answer it"

    if answer is None or answer == "":
        # We don't want to return the assumption alone if answer is empty
        return "No good Wolfram Alpha Result was found"
    return f"{assumption} --> {answer}"


if __name__ == "__main__":
    print(WolframAlphaAPIWrapper_run("Who is the PM of UK?"))
