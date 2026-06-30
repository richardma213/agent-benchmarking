import re

# Normalize query once
def normalize(q: str) -> str:
    q = q.lower().strip()
    q = q.replace("−", "-")
    q = re.sub(r"\s+", " ", q)
    return q


def parse_limit(query: str) -> bool:
    q = normalize(query)

    patterns = [
        r"limit\s",                         # "limit x->0"
        r"lim\s",                           # "lim x→0"
        r"as\s+\w+\s*(->|→|approaches)",     # "as x -> 0"
        r"approaches",                      # "approaches 0"
        r"x\s*->",                          # "x->0"
        r"x\s*→",                           # unicode arrow
    ]

    return any(re.search(p, q) for p in patterns)


def parse_diff(query: str) -> bool:
    q = normalize(query)

    patterns = [
        r"differentiate",
        r"derivative",
        r"derive",
        r"compute\s+the\s+derivative",
        r"find\s+the\s+derivative",
        r"diff\s",               # "diff sin(x)"
        r"d/dx",                 # "d/dx x^2"
        r"d\s*\w+\s*/\s*d\s*\w+",# "dy/dx"
    ]

    return any(re.search(p, q) for p in patterns)


def parse_integrate(query: str) -> bool:
    q = normalize(query)

    patterns = [
        r"integrate",
        r"antiderivative",
        r"primitive\s+function",
        r"compute\s+the\s+integral",
        r"find\s+the\s+integral",
        r"∫",                    # unicode integral
        r"integral\s+of",
        r"∫.*dx",                # "∫ x^2 dx"
        r"dx\b",                 # "x^2 dx"
        r"wrt\s*x",              # "wrt x"
        r"with\s+respect\s+to\s+x",
    ]

    return any(re.search(p, q) for p in patterns)


def parse_equation(query: str) -> bool:
    q = normalize(query)

    # Detect actual equations, not integrals or limits
    if parse_integrate(q) or parse_diff(q) or parse_limit(q):
        return False

    patterns = [
        r"=",                    # "x = 5"
        r"solve\s",              # "solve x^2 = 4"
        r"root\s+of",            # "root of equation"
        r"solution\s+to",        # "solution to x^2 = 4"
    ]

    return any(re.search(p, q) for p in patterns)