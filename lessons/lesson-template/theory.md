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

Both of these language names are supported and render as callouts:

```expected_output
ValidationError: username must not be empty
```

```expected
ValidationError: age must be between 13 and 120
```

Use these blocks when you want the learner to clearly see exact expected text.

### Blockquote

> Use blockquotes for hints, warnings, or contributor notes.

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

### 5) Use visible + hidden tests intentionally

- visible tests: learning feedback
- hidden tests: anti-cheat and edge cases

### 6) Write precise failure reasons

When a case fails, `reason` should tell the learner exactly what behavior is missing.

Bad:

- "wrong answer"

Good:

- "blank username must raise validation error"

---

## Files you must create

Every lesson must have exactly these files:

- `lesson.yaml`
- `theory.md`
- `starter.py`
- `cases.yaml`

### `lesson.yaml` template

```yaml
title: "Short lesson title"
```

Rules:

- lesson `slug` lives only in `lessons/index.yaml` and folder name
- file names are fixed by convention:
    - `theory.md`
    - `starter.py`
    - `cases.yaml`
- `title` should be short and descriptive

## Case authoring template

Recommended structure in `cases.yaml`:

```yaml
cases:
  - name: happy_path
    label: happy path
    hidden: false
    script: |
      # arrange
      # act
      # assert
      ok = True
      if not ok:
          reason = "specific actionable failure message"
```

### Case script contract (important)

Inside each `script`:

- you may use objects created in learner code
- you must set `ok` (`True`/`False`)
- set `reason` only for failures (human-readable)

If `ok` is not boolean, platform treats case as failed.

### Copy-paste patterns for common case types

#### 1) happy path

```yaml
- name: valid_input
  label: valid input
  hidden: false
  script: |
    result = SomeModel(field="value")
    ok = result.field == "value"
    if not ok:
        reason = "model should preserve valid field value"
```

#### 2) expected exception

```yaml
- name: reject_invalid_input
  label: reject invalid input
  hidden: false
  script: |
    try:
        SomeModel(field=None)
        ok = False
        reason = "invalid input must raise validation error"
    except Exception:
        ok = True
```

#### 3) boundary value

```yaml
- name: accept_boundary
  label: accept boundary value
  hidden: true
  script: |
    value = SomeModel(limit=10)
    ok = value.limit == 10
    if not ok:
        reason = "boundary value 10 should be accepted"
```

Case authoring rules:

- `name` must be unique per lesson
- `label` is shown to learners for visible cases
- `hidden: true` keeps case out of sample list
- set `ok` explicitly
- set `reason` only when failed
- keep case scripts deterministic and independent

### Anti-patterns to avoid

- vague names like `case1`, `test_a`
- reasons like `"wrong answer"` (not actionable)
- one giant case that checks everything
- random/time-based behavior in scripts
- hidden-only lessons (always keep visible feedback)

## Contributor checklist

Before opening a PR:

1. verify `lesson.yaml`, `theory.md`, `starter.py`, `cases.yaml` exist
2. verify lesson slug is added to `lessons/index.yaml`
3. run lesson sync endpoint/command and check counters
4. run tests with `uv run pytest`
5. confirm theory renders correctly in quest UI
6. confirm each visible case has clear `label` and useful `reason`

## Exercise in this template lesson

Implement `UserProfile` in starter code:

- `username: str`
- `age: int`
- `tags: list[str] = []`
- reject blank username
- accept only `13 <= age <= 120`

When all cases pass, your lesson pipeline is configured correctly.

## Contributor workflow summary

1. duplicate template lesson directory
2. define one clear objective
3. write concise theory with one `expected_output` example
4. prepare minimal starter code
5. add 2-4 visible cases and 1-3 hidden edge cases
6. sync lessons
7. open UI and run lesson manually
8. run `uv run pytest`
