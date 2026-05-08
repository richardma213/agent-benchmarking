import re

def parse_limit(query: str):
    # Matches: "limit of sin(x)/x as x approaches 0"
    match = re.search(r'limit of (.+) as (\w+) approaches ([\d\.\-]+)', query)
    if match:
        expr, var, point = match.groups()
        return f"limit({expr}, {var}, {point})"
    return None

def parse_diff(query: str):
    # Matches: "differentiate sin(x) wrt x"
    match = re.search(r'differentiate (.+) wrt (\w+)', query)
    if match:
        expr, var = match.groups()
        return f"diff({expr}, {var})"
    return None

def parse_integrate(query: str):
    # Matches: "integrate sin(x) wrt x"
    match = re.search(r'integrate (.+) wrt (\w+)', query)
    if match:
        expr, var = match.groups()
        return f"integrate({expr}, {var})"
    return None

def parse_equation(query: str):
    # Matches: "solve x^2 - 4 = 0"
    if "=" in query:
        return query
    return None