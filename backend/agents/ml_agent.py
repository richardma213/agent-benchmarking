import time
import os
from openai import OpenAI
from .base_agent import BaseAgent

class MLAgent(BaseAgent):
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
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": (
                        "Return only the final numeric answer (no latex). "
                        "Do not explain, show steps, or add context. "
                        "Output must be a valid mathematical answer (e.g., 1/2, -sin(x), sqrt(x+1)). "
                        f"Request: {problem}\nAnswer:"
                    )
                    }],
            )
            answer_text = completion.choices[0].message.content.strip()
            tokens_used = completion.usage.total_tokens if hasattr(completion, "usage") else len(problem.split()) * 2
        except Exception as e:
            answer_text = f"[ERROR] {e}"
            tokens_used = 0

        latency = time.time() - start
        return {
            "answer": answer_text,
            "tokens": tokens_used,
            "latency": latency,
        }