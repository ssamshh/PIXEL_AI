from .registry import ToolRegistry
from .router import ToolRouter
class ToolOrchestrator:
    def __init__(self,registry):
        self.registry=registry; self.router=ToolRouter()
    def available_tools(self): return self.registry.list_tools()
    def run_tool(self,name,**kwargs): return self.registry.run(name,**kwargs)
    def run_calculator(self,expression): return self.run_tool("calculator",expression=expression)
    def route(self,text):
        decision=self.router.route(text)
        if not decision: return None
        result=self.run_tool(decision["tool"],**decision["arguments"])
        return {"tool":decision["tool"],"result":result}
