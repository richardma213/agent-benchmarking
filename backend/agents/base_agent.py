class BaseAgent:
    def solve(self, problem: str) -> dict:
        """
        Returns a dict with keys:
        - answer: computed solution
        - tokens: simulated token usage
        - latency: runtime in seconds
        """
        raise NotImplementedError