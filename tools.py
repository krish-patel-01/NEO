from TOOLS.searxng_tool import SearxSearchWrapper
from TOOLS.wolfram_alpha import WolframAlphaAPIWrapper_run

def general_search(query: str) -> str:
    search = SearxSearchWrapper(
        searx_host="http://127.0.0.1:8080", k=8,
        engines=['google', 'duckduckgo','wikipedia'],
    )
    return search.run(query)

def wolfram_alpha(query: str) -> str:
    try:
        return WolframAlphaAPIWrapper_run(query)
    except:
        return "I am sorry, I could not find the answer to your query."
    # return WolframAlphaAPIWrapper_run(query)

# def calculate(operation: str) -> float:
#     return eval(operation)

# def get_planet_mass(planet) -> float:
#     match planet.lower():
#         case "earth":
#             return 5.972e24
#         case "mars":
#             return 6.39e23
#         case "jupiter":
#             return 1.898e27
#         case "saturn":
#             return 5.683e26
#         case "uranus":
#             return 8.681e25
#         case "neptune":
#             return 1.024e26
#         case "mercury":
#             return 3.285e23
#         case "venus":
#             return 4.867e24
#         case _:
#             return 0.0
        
        
if __name__ == "__main__":
    # query = "Who is the PM of UK?"
    query = "sin A = sqrt(1 - cos^2 A) and sec A = 1 / cos A, where cos A = adjacent side / hypotenuse = 8x / sqrt(8^2 + 15^2)x = 8 / sqrt(289) = 8/17"
    print(wolfram_alpha(query))