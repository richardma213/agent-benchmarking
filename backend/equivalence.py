from backend_apis import equivalent_llm
from sympy import Symbol, simplify, log, E, pi, oo, zoo
from sympy.core.sympify import SympifyError
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

TRANSFORMATIONS = standard_transformations + (convert_xor, implicit_multiplication_application)

LOCAL_DICT = {
    "ln": log,
    "log": log,
    "e": E,
    "pi": pi,
    "oo": oo,
    "zoo": zoo,
    "C": Symbol("C"),
}

def _parse_math_expression(value: str):
    normalized_value = str(value).strip()
    if not normalized_value:
        raise SympifyError("Empty expression")

    return parse_expr(
        normalized_value,
        local_dict=LOCAL_DICT,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )


def equivalent(a: str, b: str) -> bool:
    # Step 1: strict SymPy equivalence
    try:
        left = _parse_math_expression(a)
        right = _parse_math_expression(b)
        difference = simplify(left - right)
        if difference == 0:
            return True
    except Exception:
        pass

    # Step 2: LLM fallback
    return equivalent_llm(a, b)