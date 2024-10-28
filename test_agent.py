from agent import agent_loop


result = agent_loop(
    # "What is the mass of Pluto times 2?"
    query="28,800 seconds to hours",
    # verbose=False
)

print(">>>", result)
