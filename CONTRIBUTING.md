# Adding new lessons to Pydantic Quest

If you want to add a new lesson to pydantic quest, do this:

1. Create a new folder inside [lessons/](lessons/)
2. Populate the folder with 5 neccessary files. You can copy them from
   [lessons/lesson-template/](lessons/lesson-template/):
    * `lesson.yaml`
    * `theory.md`
    * `starter.py`
    * `cases.yaml`
    * `quiz.yaml`

## Directory naming rules

Lessons can have child lessons and their hierarchy is inferred from directory nesting.

Every lesson directory must start with a numeric prefix:

```text
01-introduction/
02-pydantic/
03-pydantic-vs-dataclasses/
```

Nested lessons follow the exact same rule inside their parent lesson directory:

```text
03-validators/
02-validators/01-model-validators/
02-validators/02-field-validators/
```

## How slug and order are inferred

The `slug` is inferred from the directory name **without** the numeric prefix.

Examples:

```text
02-pydantic                     -> slug: pydantic
01-dynamic-types                -> slug: dynamic-types
03-pydantic-vs-dataclasses      -> slug: pydantic-vs-dataclasses
```

The `order` is inferred from all numeric prefixes in the full path from [lessons/](lessons/) to the lesson directory.

Examples:

```text
lessons/01-introduction/                                      -> order: 1
lessons/02-pydantic/                                          -> order: 2
lessons/02-pydantic/01-dynamic-types/                         -> order: 2.1
lessons/02-pydantic/02-type-hints/                            -> order: 2.2
lessons/03-pydantic-vs-dataclasses/02-leaked-dependency/      -> order: 3.2
lessons/04-basemodel/02-type-coercion/                        -> order: 4.2
```

Practical rule:

- lesson folders must be prefixed like `01-slug-name`
- the lesson's `slug` is the part after the first dash
- lessons can have child lessons and their hierarchy is inferred from directory nesting
- order is inferred from numeric prefixes
- sibling lessons should have unique numeric prefixes
- real lesson folders should mirror the intended curriculum order in the project tree itself

## Explanation of the 5 neccessary files

### 1. `lesson.yaml`

This file currently only defines the name of the lesson. The file has the following structure:

```yaml
title: "Your lesson title goes here"
```

Change the `title` field to the title of your lesson.

### 2. `theory.md`

The contents of this file is the lesson *body:* what the user sees on the
left side of the screen when your lesson is selected.
Populate it with theoretical information and an assignment.
Refer to [lessons/lesson-template/theory.md](lessons/lesson-template/theory.md) to see available
custom formatting (on top of existing Markdown formatting)
and general recommendations on designing a good lesson body.

### 3. `starter.py`

The contents of this python script is what will be displayed to the user in the code editor
by default in your lesson.
The user will then build upon your starter script in order to complete the assignment.
Refer to [lessons/lesson-template/starter.py](lessons/lesson-template/starter.py) for better insight.

### 4. `cases.yaml`

Test cases for your lesson. Just refer to [`lessons/lesson-template/cases.yaml`](lessons/lesson-template/cases.yaml).
You can find
a *lot* of information there about how it works and how exactly to design your own test cases.
Please inform me if it is still not very clear.

This file is always required for consistency, but it can be empty.
If `cases.yaml` is empty, the lesson has no coding assignment and the `run` button will not appear in the UI.

### 5. `quiz.yaml`

Quiz questions for your lesson. Refer to [`lessons/lesson-template/quiz.yaml`](lessons/lesson-template/quiz.yaml).
If the file contains questions, the user will see a `Questions` tab in the practice panel.
If it is empty, the lesson simply has no quiz.

`cases.yaml` and `quiz.yaml` are fully independent:

- a lesson can have only coding assignment
- a lesson can have only quiz questions
- a lesson can have both
- a lesson can have neither

# Contributor checklist

Before opening a PR:

1. verify `lesson.yaml`, `theory.md`, `starter.py`, `cases.yaml`, and `quiz.yaml` exist in your new lesson folder
2. verify the lesson folder name is prefixed like `01-your-slug`
3. verify lesson folders are placed in the correct parent folder so nesting matches the intended hierarchy
4. verify sibling lessons are ordered correctly by their numeric prefixes
