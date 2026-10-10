import ast, operator, math
from .base import PixelTool

class CalculatorTool(PixelTool):
    name="calculator"
    description="Safely calculate arithmetic expressions."
    OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,
         ast.Div:operator.truediv,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,
         ast.Pow:operator.pow,ast.USub:operator.neg,ast.UAdd:operator.pos}
    def run(self, expression: str):
        try:
            if len(expression)>200: raise ValueError("Expression is too long.")
            tree=ast.parse(expression.replace("^","**"),mode="eval")
            result=self._calc(tree.body)
            if isinstance(result,float) and not math.isfinite(result): raise ValueError("Result is not finite.")
            return {"success":True,"expression":expression,"result":result}
        except Exception as exc: return {"success":False,"error":str(exc)}
    def _calc(self,node):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            if abs(node.value)>10**100: raise ValueError("Number too large.")
            return node.value
        if isinstance(node,ast.BinOp):
            op=self.OPS.get(type(node.op))
            if op is None: raise ValueError("Operator not allowed.")
            left,right=self._calc(node.left),self._calc(node.right)
            if isinstance(node.op,ast.Pow) and abs(right)>100: raise ValueError("Exponent too large.")
            result=op(left,right)
            if isinstance(result,(int,float)) and abs(result)>10**100: raise ValueError("Result too large.")
            return result
        if isinstance(node,ast.UnaryOp):
            op=self.OPS.get(type(node.op))
            if op is None: raise ValueError("Operator not allowed.")
            return op(self._calc(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")
