# Adding new lessons to Pydantic Quest

If you want to add a new lesson to pydantic quest, do this:

1. Create a new folder in [lessons/](lessons/)
2. Populate the folder with 4 neccessary files. You can copy them from
   [lessons/lesson-template/](lessons/lesson-template/):
    * `lesson.yaml`
    * `theory.md`
    * `starter.py`
    * `cases.yaml` -- *for theory-only lessons with no coding assignment, leave this file empty*
3. Head to [lessons/index.yaml](lessons/index.yaml) and add the following:

```yaml
  - slug: dash-separated-lesson-name
    order: <order>
    no_code: false   # or `true` if there is no assignment intended for the lesson
```

The `slug` must exactly match the lesson directory name in [lessons/](lessons/).
For example, this:

```yaml
  - slug: field-validators
    order: 1.1
    no_code: false
```

must correspond to this directory:

```text
lessons/field-validators/
```

The `order` field controls lesson position in the UI and now supports
hierarchical numbering.
Lesson `4.1` will be a child of lesson `4`. The UI will represent that.

Valid examples:

```yaml
  - slug: validators
    order: 1
    no_code: true

  - slug: field-validators
    order: 1.1
    no_code: false

  - slug: model-validators
    order: 1.2
    no_code: false

  - slug: models
    order: 2
    no_code: true

  - slug: basemodel
    order: 2.1
    no_code: false
```

Rules:

- use positive numeric segments separated by dots
- like this: `"1"`, `"1.1"`, `"2.3.4"`
- every order value must be unique
- set `no_code: true` for theory-only lessons with no coding task

Sorting is numeric by segment, so lessons appear like:

- `1`
- `1.1`
- `1.2`
- `2`

If you're not sure where a lesson should go, just add it near the right section
and i can reorder things myself later :)

## Explanation of the 4 neccessary files

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

If the lesson is marked `no_code: true`, this file is still required for consistency,
but it can be empty. The `run` button below the code editor will be disabled in the UI.

# Contributor checklist

Before opening a PR:

1. verify `lesson.yaml`, `theory.md`, `starter.py`, and `cases.yaml` exist in your new lesson folder
2. verify lesson slug is added to [lessons/index.yaml](lessons/index.yaml)
3. confirm each visible case has clear `label` and useful `reason`
