# trellis

Lightweight, schema-driven guardrails for AI responses.

Define your output shape with Pydantic. Write rules as plain Python functions. Trellis validates AI output against both.

## Install

```bash
pip install trellis-ai
```

## Usage

**1. Define your schema**

```python
from pydantic import BaseModel

class ChatResponse(BaseModel):
    text: str
    category: str
```

**2. Write rules in `rules.py`**

```python
from trellis import rule
from schema import ChatResponse

@rule
def no_inappropriate_content(response: ChatResponse) -> bool:
    blocked = ["spam", "scam", "fraud"]
    return not any(w in response.text.lower() for w in blocked)

@rule
def not_too_long(response: ChatResponse) -> bool:
    return len(response.text) <= 1000
```

**3. Validate AI output**

```python
import rules  # registers all @rule decorators
from trellis import Guardrail
from schema import ChatResponse

g = Guardrail(schema=ChatResponse)
result = g.validate(ai_output)

if result.passed:
    print(result.output)   # parsed ChatResponse
else:
    print(result.failures) # ["no_inappropriate_content"]
```

`g.validate()` accepts a dict or raw JSON string.

## How it works

- `@rule` registers a function into a global rule registry
- `Guardrail(schema=ChatResponse)` snapshots the registry at construction time
- `validate()` parses the AI output through Pydantic first, then runs every rule
- Returns a `ValidationResult` with `passed`, `output`, and `failures`

## License

MIT
