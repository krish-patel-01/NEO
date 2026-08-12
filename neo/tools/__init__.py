"""Tools the agent can call.

Only the callables exported here are reachable from the agent loop — see the
TOOLS dispatch table in neo/agent.py.
"""

import logging
import os

from neo.tools.searxng import SearxSearchWrapper
from neo.tools.wolfram import WolframAlphaAPIWrapper_run

logger = logging.getLogger(__name__)

SEARX_HOST = os.getenv("SEARXNG_HOST", "http://127.0.0.1:8080")


def general_search(query: str) -> str:
    """Search the web via a locally running SearXNG instance."""
    search = SearxSearchWrapper(
        searx_host=SEARX_HOST,
        k=20,
        engines=["google", "duckduckgo", "wikipedia"],
    )
    return search.run(query)


def wolfram_alpha(query: str) -> str:
    """Answer a computational or factual query via Wolfram Alpha."""
    try:
        return WolframAlphaAPIWrapper_run(query)
    except Exception as e:
        # Logged rather than swallowed silently — a bare `except: pass` here made
        # a missing API key look identical to a genuinely unanswerable question.
        logger.warning("Wolfram Alpha lookup failed for %r: %s", query, e)
        return "I am sorry, I could not find the answer to your query."


__all__ = ["general_search", "wolfram_alpha"]
