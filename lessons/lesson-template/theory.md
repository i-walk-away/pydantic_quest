Lesson body template

## How to write a good lesson body

The first lesson in the topic should be a general explanation of the concept. For example:

```
1. Validators           <--- if you are creating this (first lesson in the topic)
  1.1. Field validators
  1.2. Model validators
```

The lesson body for the main lesson in the topic should define and explain the general idea
behind the concept in question.

Like this:

"Validators are used for validating data. The rest of the body will explain the general idea
behind pydantic's validators. There are field validators, model validators and a bunch
of other things. There will be headers like 'Why use them', 'Examples' without dwelling too
much into details and so on."

---

## Markdown formatting showcase

Regular paragraph text. I will now populate this paragraph with a bunch of words.
I can't think of anything else to write. I hope you like my website.

### Emphasis

- To emphasise on a certain word, prefer *italic* over **bold**, as it is a bit nicer for the eye
- `inline code` for symbols, field names, and function calls

### Lists

1. numeric list
2. oi mate pretty rad list innit
3. thank you!

* bullet lists are not indented for some reason
* le cats are truly a gift to our wicked world

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

This block has cool custom rendering in the ui.
It's unlikely you will ever need it, but it exists

```expected_output
ValidationError: username must not be empty
```

### Horizontal rule

---

### Blockquote

> "Blockquotes", - (c) Robert J. Oppenheimer



