# Adding new lessons to Pydantic Quest

If you want to add a new lesson to pydantic quest, do this:

1. Create a new folder in [lessons/](lessons/)
2. Populate the folder with 5 neccessary files. You can copy them from
   [lessons/lesson-template/](lessons/lesson-template/):
    * `lesson.yaml`
    * `theory.md`
    * `starter.py`
    * `cases.yaml` -- *if the lesson has no coding assignment, leave this file empty*
    * `quiz.yaml` -- *if the lesson has no quiz questions, leave this file empty*
3. Head to [lessons/index.yaml](lessons/index.yaml) and add the following:

```yaml
  - slug: dash-separated-lesson-name
    order: <order>
```

The `slug` must exactly match the lesson directory name in [lessons/](lessons/).
For example, this:

```yaml
  - slug: field-validators
    order: 1.1
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

  - slug: field-validators
    order: 1.1

  - slug: model-validators
    order: 1.2

  - slug: models
    order: 2

  - slug: basemodel
    order: 2.1
    
  - slug: basemodel-settings
    order: 2.1.1
```

Rules:

- use positive numeric segments separated by dots
- like this: `"1"`, `"1.1"`, `"2.3.4"`
- every order value must be unique
- `cases.yaml` must always exist, even if it is empty
- `quiz.yaml` must always exist, even if it is empty

Sorting is numeric by segment, so lessons appear like:

- `1`
- `1.1`
- `1.2`
- `2`

If you're not sure where a lesson should go, just add it near the right section
and i can reorder things myself later :)

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
2. verify lesson is added to [lessons/index.yaml](lessons/index.yaml)

