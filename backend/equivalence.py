
from sympy import sympify, simplify

def equivalent(a: str, b: str) -> bool:
    try:
        A = sympify(a)
        B = sympify(b)
        return simplify(A - B) == 0
    except Exception:
        return False