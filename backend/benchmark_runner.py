
from agents.ml_agent import MLAgent
from agents.math_agent import MathAgent

def run_benchmark(problem: str):
    agents = {
        "ml_agent": MLAgent(),
        "math_agent": MathAgent(),  # inside, router will call parser
        #"math_agent1" : MlAgent1()  # inside, router will call parser
    }
    results = {}
    for name, agent in agents.items():
        results[name] = agent.solve(problem)
    return results