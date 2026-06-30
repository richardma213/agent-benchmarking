from backend_apis import equivalent_llm
import sympy
from sympy import (
    Symbol, sin, cos, tan, asin, acos, atan,
    sqrt, log, exp, pi, E, oo, zoo, Abs,
    gamma, Ci, Si, fresnels, fresnelc,
    asinh, acosh, atanh, simplify
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    convert_xor, implicit_multiplication_application
)
from sympy.core.sympify import SympifyError
import re
# ------------------------------------------------------------
# 1. Transformations
# ------------------------------------------------------------

TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application
)

# ------------------------------------------------------------
# 2. Expanded SymPy dictionary
# ------------------------------------------------------------

LOCAL_DICT = {
    # Variables
    "x": Symbol("x"),
    "y": Symbol("y"),
    "a": Symbol("a"),
    "b": Symbol("b"),
    "C": Symbol("C"),

    # Constants
    "pi": pi,
    "e": E,
    "E": E,
    "oo": oo,
    "zoo": zoo,
    "I": sympy.I,

    # Basic functions
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "sqrt": sqrt,
    "log": log,
    "ln": log,
    "exp": exp,
    "Abs": Abs,

    # Hyperbolic
    "asinh": asinh,
    "acosh": acosh,
    "atanh": atanh,

    # Special functions
    "gamma": gamma,
    "Ci": Ci,
    "Si": Si,
    "fresnels": fresnels,
    "fresnelc": fresnelc,

    # SymPy classes
    "Piecewise": sympy.Piecewise,
}

# ------------------------------------------------------------
# 3. Garbage detector
# ------------------------------------------------------------

def is_garbage(expr: str) -> bool:
    """
    Detect agent hallucinations that should NEVER be considered equivalent.
    """
    if not expr:
        return True

    s = str(expr).lower()

    return any([
        "nan" in s,
        "inf" in s,
        "undefined" in s,
        "piecewise" in s,
        "i(" in s,          # ml_agent hallucination
        "gamma(" in s and "expected" not in s,
        "fresnels(" in s and "expected" not in s,
        "sec^2" in s,       # ml_agent hallucination
        "e*g*i*l*n*r*t" in s,  # math_agent hallucination
        "error" in s,
        "invalid" in s,
    ])

# ------------------------------------------------------------
# 4. Normalization
# ------------------------------------------------------------
def normalize_expression(expr: str) -> str:
    if not expr:
        return ""

    s = str(expr).strip()

    # Replace unicode minus
    s = s.replace("−", "-")

    # Replace ^ with **
    s = s.replace("^", "**")

    # Remove trailing punctuation
    s = s.rstrip(".,; ")

    # Fix common hallucinations
    s = s.replace("arctan", "atan")
    s = s.replace("arcsin", "asin")
    s = s.replace("arccos", "acos")
    s = s.replace("|", "Abs")  # log(|x|) → log(Abs(x))

    # ------------------------------------------------------------
    # NEW: Strip additive constants like +C, -C, + constant, + K
    # ------------------------------------------------------------

    # Remove "+ C", "- C", "+C", "-C"
    s = re.sub(r"(\+|\-)\s*C\b", "", s)

    # Remove "+ constant", "- constant"
    s = re.sub(r"(\+|\-)\s*constant\b", "", s, flags=re.IGNORECASE)

    # Remove "+ K", "- K", etc. (generic single-letter constants)
    s = re.sub(r"(\+|\-)\s*[A-Za-z]\b", "", s)

    # Remove trailing "+ C" style constants if they appear at end
    s = re.sub(r"\bC$", "", s)

    # Remove double spaces created by stripping
    s = re.sub(r"\s+", " ", s).strip()

    return s

# ------------------------------------------------------------
# 5. Parsing
# ------------------------------------------------------------

def parse_math(expr: str):
    normalized = normalize_expression(expr)
    if not normalized:
        raise SympifyError("Empty expression")

    return parse_expr(
        normalized,
        local_dict=LOCAL_DICT,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )

# ------------------------------------------------------------
# 6. Numeric sampling fallback
# ------------------------------------------------------------

def numeric_equivalent(left, right):
    xs = [0.5, 1, 2, 3, -1, -2]

    for val in xs:
        try:
            lv = float(left.subs({"x": val}))
            rv = float(right.subs({"x": val}))
            if abs(lv - rv) > 1e-6:
                return False
        except Exception:
            return False

    return True

# ------------------------------------------------------------
# 7. Main equivalence checker
# ------------------------------------------------------------

def equivalent(a: str, b: str) -> bool:
    """
    Full equivalence checker with:
    - garbage detection
    - symbolic parsing
    - equals()
    - simplify()
    - numeric sampling
    - LLM fallback only when necessary
    """

    # 1. Garbage → never equivalent
    if is_garbage(a) or is_garbage(b):
        return False

    try:
        left = parse_math(a)
        right = parse_math(b)

        # 2. Structural equality
        if left.equals(right):
            return True

        # 3. Simplification
        diff = simplify(left - right)
        if diff == 0:
            return True

        # 4. Numeric sampling
        if numeric_equivalent(left, right):
            return True

        # 5. LLM fallback (rare)
        return False

    except Exception as e:
        print("SymPy parse error → LLM fallback:", e)
        return equivalent_llm(a, b)