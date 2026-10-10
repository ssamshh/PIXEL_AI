import re
class ToolRouter:
    """Conservative deterministic routing; only clearly arithmetic-only messages go to calculator."""
    ARITHMETIC=re.compile(r"^[\d\s+\-*/%^().]+$")
    def route(self,text):
        candidate=text.strip()
        if self.ARITHMETIC.fullmatch(candidate) and re.search(r"[+\-*/%^]",candidate):
            return {"tool":"calculator","arguments":{"expression":candidate}}
        return None
