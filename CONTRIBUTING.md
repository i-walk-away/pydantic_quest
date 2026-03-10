# Contributing

Table of contents!

## Adding new lessons to pydantic quest

If you want to add a new lesson to pydantic quest, do this:

1. Create a new folder in [lessons/](lessons/)
2. Populate the folder with 4 neccessary files. You can copy them from
   [lessons/lesson-template/](lessons/lesson-template/):
    * lesson.yaml
    * theory.md
    * starter.py
    * cases.yaml
3. Head to [lessons/index.yaml](lessons/index.yaml) and add the following:

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
That file is here: [lessons/lesson-template/theory.md](lessons/lesson-template/theory.md)

### 3. `starter.py`

The contents of this python script is what will be displayed to the user in the code editor
by default in your lesson.
The user will then build upon your starter script in order to complete the assignment.
Refer to [lessons/lesson-template/starter.py](lessons/lesson-template/starter.py) for more insight.

### 4. `cases.yaml`

Test cases for your lesson. Just refer to [`lessons/lesson-template/cases.yaml`](lessons/lesson-template/cases.yaml).
You can find
a *lot* of information there about how it works and how exactly to design your own test cases.
Please inform me if it is still not very clear.

## Contributor checklist

Before opening a PR:

1. verify `lesson.yaml`, `theory.md`, `starter.py`, and `cases.yaml` exist in your new lesson folder
2. verify lesson slug is added to [lessons/index.yaml](lessons/index.yaml)
3. confirm each visible case has clear `label` and useful `reason`
