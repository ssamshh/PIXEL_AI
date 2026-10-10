"""Example local plugin. Plugins are executable Python; review before enabling."""
class ExamplePlugin:
    name = "example"
    description = "Example plugin loaded by PIXEL's local plugin manager."
    def run(self, **kwargs):
        return {"success": True, "message": "Example plugin is ready."}

plugin = ExamplePlugin()
