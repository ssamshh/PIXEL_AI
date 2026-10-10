import importlib.util
from pathlib import Path

class PluginManager:
    """Loads local Python plugins from plugins/*.py. Only load code you trust."""
    def __init__(self, directory=None):
        self.directory=Path(directory or Path(__file__).resolve().parent.parent/"plugins")
        self.plugins={}
    def discover(self):
        self.directory.mkdir(parents=True,exist_ok=True)
        found=[]
        for path in sorted(self.directory.glob("*.py")):
            if path.name.startswith("_"): continue
            name=path.stem
            try:
                spec=importlib.util.spec_from_file_location(f"pixel_user_plugin_{name}",path)
                if not spec or not spec.loader: continue
                module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                plugin=getattr(module,"plugin",None)
                if plugin is not None:
                    self.plugins[name]=plugin
                    found.append({"name":name,"description":getattr(plugin,"description","Local plugin")})
            except Exception as exc:
                found.append({"name":name,"error":str(exc)})
        return found
