from typing import Callable, Dict, Any


class CallbackRegistry:
    def __init__(self):
        self._callbacks: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]):
        self._callbacks[name] = func

    def call(self, expression: str, context: Dict[str, Any]):
        """
        expression example:
            sistema = arcprob_SP_2(x1,x2,Prob)
        """
        if "=" in expression:
            lhs, rhs = expression.split("=", 1)
            lhs = lhs.strip()
        else:
            lhs = None
            rhs = expression

        name = rhs.split("(")[0].strip()

        if name not in self._callbacks:
            raise ValueError(f"Callback '{name}' not registered")

        result = self._callbacks[name]()

        if lhs:
            context[lhs] = result

        return result
