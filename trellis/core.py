from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

_registry: list[Rule] = []


class Rule:
    def __init__(self, fn: Callable, name: str | None = None):
        self.fn = fn
        self.name = name or fn.__name__

    def check(self, model: BaseModel) -> bool:
        return bool(self.fn(model))


def rule(fn: Callable) -> Rule:
    """Decorator that registers a function as a trellis rule."""
    r = Rule(fn)
    _registry.append(r)
    return r


@dataclass
class ValidationResult:
    passed: bool
    output: BaseModel | None
    failures: list[str] = field(default_factory=list)


class Guardrail:
    def __init__(self, schema: type[BaseModel], rules: list[Rule] | None = None):
        self.schema = schema
        self.rules = rules if rules is not None else list(_registry)

    def validate(self, data: dict | str | Any) -> ValidationResult:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return ValidationResult(passed=False, output=None, failures=["invalid_json"])

        try:
            model = self.schema.model_validate(data)
        except ValidationError:
            return ValidationResult(passed=False, output=None, failures=["schema_validation"])

        failures = [r.name for r in self.rules if not r.check(model)]

        return ValidationResult(
            passed=not failures,
            output=model if not failures else None,
            failures=failures,
        )
