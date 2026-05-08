import re
import os

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from .parser import parse_limit, parse_diff, parse_integrate, parse_equation

if load_dotenv is not None:
    load_dotenv()

class LLMParser:
    def __init__(self, model_name="google/gemma-4-31B-it:novita", hf_token=None):
        self.model_name = model_name
        self.hf_token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")

        # Initialize Hugging Face router client (OpenAI-style)
        if OpenAI and self.hf_token:
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.hf_token,
            )
        else:
            self.client = None

    def _build_prompt(self, query: str) -> str:
    
        return (
            "Return only the final SymPy expression. "
            "Do not explain, simplify, or evaluate. "
            "Output must be valid SymPy syntax (e.g., Rational(1,2), sin(x), diff(expr,var)). "
            f"Request: {query}\nSymPy:"
        )

    def _normalize_expression(self, expr: str, var: str | None = None):
        normalized = expr.strip().lower()
        replacements = {
            r"\bsine\b": "sin",
            r"\bcosine\b": "cos",
            r"\btangent\b": "tan",
            r"\bcosecant\b": "csc",
            r"\bsecant\b": "sec",
            r"\bcotangent\b": "cot",
        }
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        if var and normalized in {"sin", "cos", "tan", "sec", "csc", "cot"}:
            return f"{normalized}({var})"
        return normalized

    def _extract_sympy_candidate(self, text: str, query: str):
        cleaned = text.strip()
        if not cleaned:
            return None
        limit_match = re.search(r"limit\((.+?),\s*(\w+),\s*(.+?)\)", cleaned)
        if limit_match:
            expr, var, point = limit_match.groups()
            return f"limit({self._normalize_expression(expr, var)}, {var}, {point.strip()})"
        diff_match = re.search(r"diff\((.+?),\s*(\w+)\)", cleaned)
        if diff_match:
            expr, var = diff_match.groups()
            return f"diff({self._normalize_expression(expr, var)}, {var})"
        integrate_match = re.search(r"integrate\((.+?),\s*(\w+)\)", cleaned)
        if integrate_match:
            expr, var = integrate_match.groups()
            return f"integrate({self._normalize_expression(expr, var)}, {var})"
        eq_match = re.search(r"(.+?\s*=\s*.+)", cleaned)
        if eq_match:
            return eq_match.group(1).strip()
        return cleaned

    def _heuristic_parse(self, query: str):
        parsed = self._extract_sympy_candidate(query, query)
        if parsed and parsed != query.strip():
            return parsed
        if "=" in query:
            return query.strip()
        return None

    def _query_remote(self, prompt: str):
        if not self.client:
            return None
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            content = completion.choices[0].message.content.strip()
            tokens = None
            try:
                tokens = completion.usage.total_tokens
            except Exception:
                tokens = None
            return content, tokens
        except Exception as e:
            print("[DEBUG] Router request failed:", e)
            return None, None

    def parse(self, query: str):
        # Step 1: Try regex functions first
        for fn in (parse_limit, parse_diff, parse_integrate, parse_equation):
            candidate = fn(query)
            if candidate:
                # Regex-based parse — count as 1 token usage for the parser
                return candidate, 1

        # Step 2: Fallback to remote LLM
        prompt = self._build_prompt(query)
        generated_text, tokens = self._query_remote(prompt)
        if generated_text:
            parsed_candidate = self._extract_sympy_candidate(generated_text, query)
            if parsed_candidate:
                # If remote returned token usage, forward it; otherwise leave as 0
                return parsed_candidate, (tokens if tokens is not None else 0)

        # Step 3: Final fallback — best-effort deterministic parse
        parsed = self._heuristic_parse(query)
        # Deterministic fallback treated as regex parser (1 token)
        return parsed, 1
