import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

MODEL_NAME = "qwen2.5-3b-instruct"

def equivalent_llm(a: str, b: str) -> bool:
    prompt = f"""
    Determine whether the following two mathematical expressions are mathematically equivalent.

    Expression A:
    {a}

    Expression B:
    {b}

    Rules:
    - Compare the expressions as mathematical answers, not as strings.
    - Treat equivalent algebraic forms as equivalent.
    - If there is any doubt, return false.
    - Output only valid JSON: {{"equivalent": true}} or {{"equivalent": false}}.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict mathematical equivalence checker."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
    except Exception as e:
        print("LLM fallback error:", e)
        return False

    content = (response.choices[0].message.content or "").strip()

    try:
        parsed = json.loads(content)
        return bool(parsed.get("equivalent", False))
    except Exception:
        normalized = content.lower()
        return "true" in normalized or "equivalent" in normalized