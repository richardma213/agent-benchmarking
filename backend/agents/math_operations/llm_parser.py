import os

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


class LLMParser:
    def __init__(self, model_name="qwen2.5-7b-instruct-1m", local=True, hf_token=None):
        self.model_name = model_name

        if local:
            # Use LM Studio local server
            self.client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="lm-studio",  # LM Studio ignores this
            )
        else:
            # Use HuggingFace Router
            self.hf_token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not self.hf_token:
                raise ValueError("HF token required when local=False")

            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.hf_token,
            )

    # ---------------------------------------------------------
    # Generic prompt
    # ---------------------------------------------------------
    def _build_prompt(self, query: str) -> str:
        return (
            "Return only the final SymPy expression. "
            "Do not explain, simplify, or evaluate. "
            "Output must be valid SymPy syntax. "
            f"Request: {query}\nSymPy:"
        )

    # ---------------------------------------------------------
    # Type-aware prompt
    # ---------------------------------------------------------
    def _build_prompt_with_type(self, query: str, problem_type: str) -> str:
        return (
            "Return only the final SymPy expression. "
            "Do not explain, simplify, or evaluate. "
            "Output must be valid SymPy syntax. "
            f"Format as {problem_type}(...) form. "
            f"Request: {query}\nSymPy:"
        )

    # ---------------------------------------------------------
    # Remote call
    # ---------------------------------------------------------
    def _query_remote(self, prompt: str):
        if not self.client:
            return None, None

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            content = completion.choices[0].message.content.strip()

            try:
                tokens = completion.usage.total_tokens
            except Exception:
                tokens = None

            return content, tokens

        except Exception as e:
            print("[DEBUG] Router request failed:", e)
            return None, None

    # ---------------------------------------------------------
    # Public API: generic parse
    # ---------------------------------------------------------
    def parse(self, query: str):
        prompt = self._build_prompt(query)
        return self._query_remote(prompt)

    # ---------------------------------------------------------
    # Public API: type-aware parse
    # ---------------------------------------------------------
    def parse_with_type(self, query: str, problem_type: str):
        prompt = self._build_prompt_with_type(query, problem_type)
        return self._query_remote(prompt)

    # ---------------------------------------------------------
    # NEW: Auto-repair for invalid SymPy output
    # ---------------------------------------------------------
    def repair(self, bad_output: str):
        """
        Attempt to fix invalid SymPy output using a minimal repair prompt.
        This is only called when sympify() fails.
        """
        prompt = (
            "Fix this to valid SymPy only. "
            "No text, no steps, no explanation. "
            f"Broken: {bad_output}\n"
            "SymPy:"
        )
        return self._query_remote(prompt)

