## Markdown formatting showcase

Regular paragraph text should explain intent first, then constraints.

### Emphasis

- **bold** for critical constraints
- *italic* for nuance
- `inline code` for symbols, field names, and function calls

### Lists

1. use numbered lists for step-by-step tasks
2. keep each item short and explicit
3. include acceptance criteria in plain language

- use bullet lists for examples and notes
- keep one idea per bullet

### Code blocks

```python
from pydantic import BaseModel, field_validator


class UserProfile(BaseModel):
    username: str
    age: int
    tags: list[str] = []

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username must not be empty")
        return normalized
```

### Expected output block

This block has cool custom rendering in the ui. Use it to define the expected output:

```expected_output
ValidationError: username must not be empty
```

### Blockquote

> Use blockquotes for hints, warnings, or notes.

### Horizontal rule

---

## Lesson order in `lessons/index.yaml`

The lesson list supports hierarchical numbering.

Use an `order` path like:

```yaml
lessons:
  - slug: validators
    order: "1"
  - slug: field-validators
    order: "1.1"
  - slug: model-validators
    order: "1.2"
  - slug: models
    order: "2"
```

Rules:

- each segment must be a positive integer
- use dots for nesting
- every order must be unique
- quote dotted values like `"1.1"` in YAML

Sorting is numeric by segment, so `1.10` comes after `1.2`, not before it.

---

## How to write a good lesson

### 1) Define one learning objective

Good:

- "Use `field_validator` to reject blank strings."

Too broad:

- "Learn Pydantic validators."
