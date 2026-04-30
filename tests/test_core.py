import pytest
from pydantic import BaseModel

from trellis import Guardrail, rule
from trellis.core import _registry


class Response(BaseModel):
    text: str


@pytest.fixture(autouse=True)
def clear_registry():
    _registry.clear()
    yield
    _registry.clear()


def test_passes_when_all_rules_pass():
    @rule
    def always_pass(r: Response) -> bool:
        return True

    result = Guardrail(schema=Response).validate({"text": "hello"})
    assert result.passed
    assert result.output.text == "hello"
    assert result.failures == []


def test_fails_when_rule_fails():
    @rule
    def always_fail(r: Response) -> bool:
        return False

    result = Guardrail(schema=Response).validate({"text": "hello"})
    assert not result.passed
    assert result.output is None
    assert "always_fail" in result.failures


def test_fails_on_schema_mismatch():
    result = Guardrail(schema=Response).validate({"wrong_field": "hello"})
    assert not result.passed
    assert "schema_validation" in result.failures


def test_accepts_json_string():
    @rule
    def always_pass(r: Response) -> bool:
        return True

    result = Guardrail(schema=Response).validate('{"text": "hello"}')
    assert result.passed


def test_fails_on_invalid_json():
    result = Guardrail(schema=Response).validate("not json")
    assert not result.passed
    assert "invalid_json" in result.failures


def test_multiple_failures_reported():
    @rule
    def fail_one(r: Response) -> bool:
        return False

    @rule
    def fail_two(r: Response) -> bool:
        return False

    result = Guardrail(schema=Response).validate({"text": "hello"})
    assert "fail_one" in result.failures
    assert "fail_two" in result.failures
