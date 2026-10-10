from pixel.tools.calculator import CalculatorTool
from pixel.tools.registry import ToolRegistry
from pixel.tools.orchestrator import ToolOrchestrator

def test_calculator():
    assert CalculatorTool().run("10 + 5 * 2")["result"] == 20
    assert CalculatorTool().run("(25 + 17) * 2")["result"] == 84

def test_calculator_rejects_code():
    assert not CalculatorTool().run("__import__('os').system('echo unsafe')")["success"]

def test_registry_and_router():
    registry=ToolRegistry()
    registry.register(CalculatorTool())
    orchestrator=ToolOrchestrator(registry)
    assert orchestrator.route("15 * 8")["result"]["result"] == 120
    assert orchestrator.route("hello PIXEL") is None
