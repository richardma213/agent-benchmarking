from sympy import sympify
from . import parser
from .llm_parser import LLMParser
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

# Allow implicit multiplication like 2x → 2*x
TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

LOCAL_DICT = {
    "x": sp.Symbol("x"),
    "y": sp.Symbol("y"),

    # functions
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "exp": sp.exp,

    # calculus
    "diff": sp.diff,
    "Integral": sp.Integral,
    "Limit": sp.Limit,

    # equations
    "Eq": sp.Eq,
}

llm_parser = LLMParser()

def _dispatch_sympy(expr):
    try:
        # If it's an equation, solve it
        if isinstance(expr, sp.Equality):
            sol = sp.solve(expr)
            # Return single solution cleanly
            if len(sol) == 1:
                return sol[0]
            return sol

        # Otherwise, evaluate normally
        return expr.doit()

    except Exception:
        return expr

def validate_sympy(expr_str: str):
    try:
        return parse_expr(
            expr_str,
            local_dict=LOCAL_DICT,
            transformations=TRANSFORMS,
            evaluate=True
        )
    except Exception as e:
        print("VALIDATION ERROR:", e)
        return None

def clean_expr(expr: str) -> str:
    expr = expr.strip()

    # ---- Remove code fences / backticks ----
    if expr.startswith("```"):
        expr = expr.strip("`")
        expr = expr.replace("python", "", 1).strip()

    if expr.startswith("`") and expr.endswith("`"):
        expr = expr[1:-1].strip()

    expr = expr.replace("`", "")

    # ---- Fix equation hallucinations ----
    expr = expr.replace("equation(", "Eq(")
    expr = expr.replace("Equation(", "Eq(")
    expr = expr.replace("==", "=")

    # ---- Fix dot-notation derivatives ----
    # Rewrite "diff.xxx(y)" → "diff(xxx(y), x)"
    expr = re.sub(r"diff\.(\w+)\(([^)]+)\)", r"diff(\1(\2), x)", expr)

    return expr

def route(problem: str):
    parsed = None
    parser_tokens = 0
    problem_type = None

    # 1. classify only
    if parser.parse_limit(problem):
        problem_type = "limit"
    elif parser.parse_diff(problem):
        problem_type = "diff"
    elif parser.parse_integrate(problem):
        problem_type = "integrate"
    elif parser.parse_equation(problem):
        problem_type = "equation"

    # 2. LLM parsing (type-aware)
    try:
        if problem_type:
            parsed, tokens = llm_parser.parse_with_type(problem, problem_type)
        else:
            parsed, tokens = llm_parser.parse(problem)
        parser_tokens = tokens or 0
    except Exception:
        parsed = None

    if not parsed:
        return {
            "answer": f"Error: could not parse '{problem}'",
            "parser_tokens": 0,
            "sympy_tokens": 0,
        }

    # ---------------------------------------------------------
    # 3. VALIDATION + AUTO-REPAIR LOOP
    # ---------------------------------------------------------
    parsed = clean_expr(parsed)
    expr = validate_sympy(parsed)

    if expr is None:
        # Attempt repair
        repaired, repair_tokens = llm_parser.repair(parsed)

        if repaired:
            repaired = clean_expr(repaired)
            expr = validate_sympy(repaired)
            parser_tokens += repair_tokens or 0

        if expr is None:
            return {
                "answer": f"Error: invalid SymPy after repair: {parsed}",
                "parser_tokens": parser_tokens,
                "sympy_tokens": 0,
            }

        # Use repaired expression
        parsed = repaired

    # ---------------------------------------------------------
    # 4. Evaluate safely
    # ---------------------------------------------------------
    try:
        result = _dispatch_sympy(expr)
        return {
            "answer": result,
            "parser_tokens": parser_tokens,
            "sympy_tokens": 1,
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "parser_tokens": parser_tokens,
            "sympy_tokens": 0,
        }