import re

def parse_limit(query: str):
    # Detects "limit ... as x->0" or "limit of ... as x approaches 0"
    return bool(re.search(r'limit(?: of)? .+ as \w+ (?:->|approaches) ', query))


def parse_diff(query: str):
    # Detects "differentiate sin(x) wrt x" or "diff sin(x) x"
    return bool(re.search(r'(?:differentiate|diff) ', query))


def parse_integrate(query: str):
    # Detects "integrate ..." (with or without wrt)
    return bool(re.search(r'integrate ', query))


def parse_equation(query: str):
    # Detects "=" anywhere
    return "=" in query