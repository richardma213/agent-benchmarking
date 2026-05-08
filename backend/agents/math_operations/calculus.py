import sympy as sp

def differentiate(expr_str: str, var: str = "x"):
    x = sp.symbols(var)
    expr = sp.sympify(expr_str)
    return sp.diff(expr, x)

def integrate(expr_str: str, var: str = "x"):
    x = sp.symbols(var)
    expr = sp.sympify(expr_str)
    return sp.integrate(expr, x)

def limit(expr_str: str, var: str = "x", point = 0):
    x = sp.symbols(var)
    expr = sp.sympify(expr_str)
    return sp.limit(expr, x, sp.sympify(point))