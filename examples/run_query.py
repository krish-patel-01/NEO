"""Send a single query through the agent loop.

Makes live Groq and SearXNG calls, so it needs a configured .env and a running
SearXNG instance. This is a smoke check, not a unit test.

    python examples/run_query.py "28,800 seconds to hours"
"""

import sys

from neo.agent import agent_loop

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "28,800 seconds to hours"
    print(">>>", agent_loop(query=query))
