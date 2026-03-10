# Contributing

Table of contents!

## Adding new lessons to pydantic quest

If you want to add a new lesson to pydantic quest, do this:

1. Create a new folder in `/lessons/`
2. Populate the folder with 4 neccessary files (just copy and paste them from `lesson-template` lesson):
    * lesson.yaml
    * theory.md
    * starter.py
    * cases.yaml
3. Head to `lessons/index.yaml` and add the following:

```yaml
  - slug: dash-separated-lesson-name
    order: <integer>
```

The "order" field changes the order in which lessons appear in pydantic quest.
If you're not sure, just use whatever highest order already exists in index and
add +1 to it. I will reorder everything myself if needed :)

## Explanation of the 4 neccessary files

### 1. `lesson.yaml`

This file currently only defines the name of the lesson. The file has the following structure:

```yaml
title: "Your lesson title goes here"
```

Change the `title` field to the title of your lesson.

### 2. `theory.md`

The contents of this file is the lesson *body*: what the user sees on the
left side of the screen when your lesson is selected.
Populate it with theoretical information and an assignment.
Refer to `theory.md` file of the `lesson-template` lesson to see available
custom formatting (on top of existing Markdown formatting)
and general recommendations on designing a good lesson body.

### 3. `starter.py`

The contents of this python script is what will be displayed to the user in the code editor
by default in your lesson.
The user will then build upon your starter script in order to complete the assignment.
Refer to `starter.py` of `lesson-template` for more better insight.

### 4. `cases.yaml`

Test cases for your lesson. Just refer to the `cases.yaml` of `lesson-template`. You can find
a *lot* of information there about how it works and how exactly to design your own test cases.
Please inform me if it is still not very clear.

###################################

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

## How to write a good lesson

### 1) Define one learning objective

Good:

- "Use `field_validator` to reject blank strings."

Too broad:

- "Learn Pydantic validators."

### 2) Keep scope tight

A single lesson should focus on one concept family.
Move advanced edge-cases into hidden tests instead of overloading theory.

### 3) Provide executable acceptance criteria

Learners should be able to answer:

- What exactly must pass?
- What exactly must fail?

### 4) Make starter code minimal but directional

Starter code should:

- include target class/function names
- avoid solving the full task
- hint at expected structure


## Contributor checklist

Before opening a PR:

1. verify `lesson.yaml`, `theory.md`, `starter.py`, `cases.yaml` exist in your new lesson folder
2. verify lesson slug is added to `lessons/index.yaml`
3. confirm each visible case has clear `label` and useful `reason`

