from .base import PixelTool
class ToolRegistry:
    def __init__(self): self.tools={}
    def register(self,tool:PixelTool):
        if not tool.name or not tool.name.replace("_","").replace("-","").isalnum():
            raise ValueError("Tool name must be a simple identifier.")
        self.tools[tool.name]=tool
    def get(self,name): return self.tools.get(name)
    def list_tools(self): return [{"name":t.name,"description":t.description} for t in self.tools.values()]
    def run(self,name,**kwargs):
        tool=self.get(name)
        if not tool: return {"success":False,"error":f"Tool '{name}' not found."}
        try: return tool.run(**kwargs)
        except Exception as exc: return {"success":False,"error":str(exc)}
