import sympy as sp

def evaluate(expr_str: str):
    """
    Evaluate arithmetic or algebraic expressions numerically.
    Example: "2+2*3" -> 8.0
    """
    expr = sp.sympify(expr_str)
    return expr.evalf()