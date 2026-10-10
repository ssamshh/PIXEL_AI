from .base import PixelTool
class WebSearchTool(PixelTool):
    name="web_search"
    description="Search the public web using the optional ddgs package."
    def run(self, query: str, max_results: int=5):
        try:
            from ddgs import DDGS
        except ImportError:
            return {"success":False,"error":"Web search dependency missing. Install with: pip install -e '.[search]' "}
        try:
            results=list(DDGS().text(query,max_results=max(1,min(10,int(max_results)))))
            return {"success":True,"query":query,"results":[{"title":r.get("title",""),"url":r.get("href",""),"snippet":r.get("body","")} for r in results]}
        except Exception as exc:
            return {"success":False,"error":f"Web search failed: {exc}"}
