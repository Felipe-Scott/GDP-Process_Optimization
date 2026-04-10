from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from gdp.model import GDPModelIR


CALL_EXPR_RE = re.compile(
    r"^(?:(?P<lhs>\[[^\]]+\]|[A-Za-z_][A-Za-z0-9_]*)\s*=\s*)?"
    r"(?P<func>[A-Za-z_][A-Za-z0-9_]*)\((?P<args>.*)\)\s*;?$"
)


@dataclass(slots=True)
class ExecutionContext:
    values: Dict[str, Any] = field(default_factory=dict)

    def get(self, name: str, default: Any = None) -> Any:
        return self.values.get(name, default)

    def set(self, name: str, value: Any) -> None:
        self.values[name] = value


class PythonCallbackRegistry:
    def __init__(self):
        self._callbacks: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]) -> None:
        self._callbacks[name] = func

    def execute(self, expression: str, context: ExecutionContext, hysys: Any = None) -> Any:
        parsed = self._parse_expression(expression)
        callback = self._callbacks.get(parsed["func"])
        if callback is None:
            raise KeyError(f"Callback '{parsed['func']}' is not registered")

        args = [self._resolve_argument(arg, context) for arg in parsed["args"]]
        result = callback(context=context, hysys=hysys, *args)

        lhs = parsed["lhs"]
        if lhs is None:
            return result

        if isinstance(lhs, list):
            if not isinstance(result, (list, tuple)):
                raise TypeError(
                    f"Callback returned scalar result, but vector assignment requested: {expression}"
                )
            if len(lhs) != len(result):
                raise ValueError(
                    f"Callback returned {len(result)} values for {len(lhs)} assignment targets"
                )
            for name, value in zip(lhs, result):
                context.set(name, value)
        else:
            context.set(lhs, result)
        return result

    def _parse_expression(self, expression: str) -> Dict[str, Any]:
        match = CALL_EXPR_RE.match(expression.strip())
        if not match:
            raise ValueError(f"Unsupported callback expression: {expression}")
        args_text = match.group("args").strip()
        lhs = match.group("lhs")
        return {
            "lhs": self._parse_lhs(lhs),
            "func": match.group("func"),
            "args": self._split_args(args_text),
        }

    def _parse_lhs(self, lhs: Optional[str]) -> Optional[Any]:
        if lhs is None:
            return None
        lhs = lhs.strip()
        if lhs.startswith("[") and lhs.endswith("]"):
            inner = lhs[1:-1].strip()
            return [part.strip() for part in inner.split(",") if part.strip()]
        return lhs

    def _split_args(self, args_text: str) -> List[str]:
        if not args_text:
            return []
        args: List[str] = []
        depth = 0
        current: List[str] = []
        for char in args_text:
            if char == "," and depth == 0:
                token = "".join(current).strip()
                if token:
                    args.append(token)
                current = []
                continue
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            current.append(char)
        tail = "".join(current).strip()
        if tail:
            args.append(tail)
        return args

    def _resolve_argument(self, token: str, context: ExecutionContext) -> Any:
        token = token.strip().rstrip(";")
        if token in context.values:
            return context.values[token]
        try:
            return ast.literal_eval(token)
        except Exception:
            return token


class GDPExecutor:
    def __init__(
        self,
        model: GDPModelIR,
        callback_registry: Optional[PythonCallbackRegistry] = None,
        hysys: Any = None,
    ) -> None:
        self.model = model
        self.callback_registry = callback_registry or PythonCallbackRegistry()
        self.hysys = hysys
        self.context = ExecutionContext()

    def initialize_from_model(self) -> None:
        for init in self.model.initials:
            self._consume_assignment(init.expression)
        for bound in self.model.bounds:
            if "=" in bound.expression and "<" not in bound.expression and ">" not in bound.expression:
                self._consume_assignment(bound.expression)

    def _consume_assignment(self, expression: str) -> None:
        parts = expression.split("=", 1)
        if len(parts) != 2:
            return
        lhs = parts[0].strip().rstrip(";")
        rhs = parts[1].strip().rstrip(";")
        try:
            value = ast.literal_eval(rhs)
        except Exception:
            value = rhs
        self.context.set(lhs, value)

    def run_callbacks(self) -> Dict[str, Any]:
        for callback in self.model.callbacks:
            self.callback_registry.execute(callback.expression, self.context, self.hysys)
        return dict(self.context.values)

    def run(self) -> Dict[str, Any]:
        self.initialize_from_model()
        return self.run_callbacks()
