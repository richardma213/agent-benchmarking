import time
from .base_agent import BaseAgent
from .math_operations import router
from openai import OpenAI

class MathAgent(BaseAgent):
    def __init__(self, model_name="qwen2.5-3b-instruct", local=True, hf_token=None):
        self.model_name = model_name

        if local:
            # LM Studio local server
            self.client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="lm-studio",  # dummy key
            )
        else:
            # Hugging Face Router fallback
            self.hf_token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.hf_token,
            )

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