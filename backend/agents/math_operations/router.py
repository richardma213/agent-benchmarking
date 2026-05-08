from . import arithmetic, equations, calculus, parser
from .llm_parser import LLMParser

llm_parser = LLMParser()


def _dispatch_sympy(problem: str):
    if "=" in problem:
        return equations.solve_equation(problem)

    if problem.startswith("diff("):
        inside = problem[5:-1]
        expr_str, var = [p.strip() for p in inside.split(",")]
        return calculus.differentiate(expr_str, var)

    if problem.startswith("integrate("):
        inside = problem[10:-1]
        expr_str, var = [p.strip() for p in inside.split(",")]
        return calculus.integrate(expr_str, var)

    if problem.startswith("limit("):
        inside = problem[6:-1]
        expr_str, var, point = [p.strip() for p in inside.split(",")]
        return calculus.limit(expr_str, var, point)

    return arithmetic.evaluate(problem)

def route(problem: str):
    # Try deterministic/regex parsers first and count them as 1 token if they match
    parsed = None
    parser_tokens = 0

    for fn in (parser.parse_limit, parser.parse_diff, parser.parse_integrate, parser.parse_equation):
        candidate = fn(problem)
        if candidate:
            parsed = candidate
            parser_tokens = 1
            break

    # If no regex parser matched, use the LLM parser which returns (parsed, tokens)
    if not parsed:
        parsed, tokens = llm_parser.parse(problem)
        # llm_parser.parse now returns (parsed, tokens) — if tokens is None, treat as 0
        parser_tokens = tokens or 0

    if not parsed:
        return {
            "answer": f"Error: could not parse '{problem}'",
            "parser_tokens": 0,
            "sympy_tokens": 0,
        }

    try:
        result = _dispatch_sympy(parsed)
        # Count sympy execution as 1 token
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