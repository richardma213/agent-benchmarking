import time
from .base_agent import BaseAgent
from .math_operations import router

class MathAgent(BaseAgent):
    def solve(self, problem: str) -> dict:
        start = time.time()
        try:
            route_result = router.route(problem)
            # router.route now returns a dict with answer, parser_tokens, sympy_tokens
            if isinstance(route_result, dict):
                answer = route_result.get("answer")
                parser_tokens = route_result.get("parser_tokens", 0) or 0
                sympy_tokens = route_result.get("sympy_tokens", 0) or 0
                tokens_used = parser_tokens + sympy_tokens
            else:
                answer = route_result
                tokens_used = len(problem.split())
        except Exception as e:
            answer = f"Error: {str(e)}"
            tokens_used = 0

        latency = time.time() - start
        return {
            "answer": str(answer),
            "tokens": tokens_used,
            "latency": latency
        }