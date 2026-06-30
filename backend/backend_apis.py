import json
import os
from openai import OpenAI

MODEL_NAME = "qwen2.5-3b-instruct"

def equivalent_llm(a: str, b: str, local=True, hf_token=None) -> bool:
    """
    LLM fallback for mathematical equivalence checking.
    Can run locally (LM Studio) or on Hugging Face cloud.
    """

    # -----------------------------
    # Choose backend
    # -----------------------------
    if local:
        client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio"  # dummy key
        )
    else:
        token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token
        )

    # -----------------------------
    # Prompt
    # -----------------------------
    prompt = f"""
You must determine whether Expression A and Expression B are mathematically equivalent.

Expression A:
{a}

Expression B:
{b}

INSTRUCTIONS (STRICT):
- Think silently.
- Do NOT explain your reasoning.
- Do NOT output steps.
- Do NOT output text outside JSON.
- Respond ONLY with one of the following JSON objects:
  {{"equivalent": true}}
  {{"equivalent": false}}
"""

    # -----------------------------
    # LLM call
    # -----------------------------
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict mathematical equivalence checker. You output ONLY JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
    except Exception as e:
        print("LLM fallback error:", e)
        return False

    # -----------------------------
    # Parse JSON
    # -----------------------------
    content = (response.choices[0].message.content or "").strip()

    try:
        parsed = json.loads(content)
        return bool(parsed.get("equivalent", False))
    except Exception:
        normalized = content.lower()
        return "true" in normalized or "equivalent" in normalized
