from backend_apis import equivalent_llm
from sympy import Symbol, simplify, log, E, pi, oo, zoo
from sympy.core.sympify import SympifyError
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

# ------------------------------------------------------------
# 1. SymPy parsing configuration
# ------------------------------------------------------------

TRANSFORMATIONS = standard_transformations + (
    convert_xor,                       # allow ^ for exponentiation
    implicit_multiplication_application # allow implicit multiplication
)

LOCAL_DICT = {
    "ln": log,
    "log": log,
    "e": E,
    "pi": pi,
    "oo": oo,
    "zoo": zoo,
    "C": Symbol("C"),
}

# ------------------------------------------------------------
# 2. Syntax normalization layer (critical!)
# ------------------------------------------------------------

def normalize_expression(expr: str) -> str:
    """
    Normalize common agent output issues so SymPy can parse reliably.
    """
    if expr is None:
        return ""

    s = str(expr).strip()

    # Replace ^ with ** (even though convert_xor handles it, this is safer)
    s = s.replace("^", "**")

    # Replace unicode minus with ASCII minus
    s = s.replace("−", "-")

    # Remove accidental double spaces
    while "  " in s:
        s = s.replace("  ", " ")

    # Remove trailing periods or commas
    s = s.rstrip(".,; ")

    return s


# ------------------------------------------------------------
# 3. SymPy parsing
# ------------------------------------------------------------

def _parse_math_expression(value: str):
    normalized = normalize_expression(value)

    if not normalized:
        raise SympifyError("Empty expression")

    return parse_expr(
        normalized,
        local_dict=LOCAL_DICT,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )


# ------------------------------------------------------------
# 4. Combined equivalence checker (SymPy + LLM fallback)
# ------------------------------------------------------------

def equivalent(a: str, b: str) -> bool:
    """
    First try strict symbolic equivalence via SymPy.
    If SymPy fails OR cannot simplify to zero, fall back to LLM.
    """

    try:
        left = _parse_math_expression(a)
        right = _parse_math_expression(b)

        difference = simplify(left - right)

        # If SymPy proves equivalence, return True
        if difference == 0:
            return True

        # SymPy parsed both expressions but they differ → try LLM fallback
        return equivalent_llm(a, b)

    except Exception as e:
        # SymPy failed to parse → fallback to LLM
        print(f"SymPy parse error, falling back to LLM: {e}")
        return equivalent_llm(a, b)