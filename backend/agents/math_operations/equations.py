import sympy as sp

def solve_equation(expr_str: str):
    """
    Solve equations of the form 'lhs = rhs'.
    Example: "x**2 - 4 = 0" -> [-2, 2]
    """
    lhs, rhs = expr_str.split("=")
    x = sp.symbols('x')
    return sp.solve(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)), x)