## Validation error

We've used the term "Validation error" for quite a while now without really explaining it. In this lesson, you will
learn what it is and some cases when it is raised by Pydantic.

As a quick refresher, _data validation_ in Pydantic refers to the process of instantiating a
model that adheres to specified types and constraints. These types and constraints are set by... You!

When you define a BaseModel like this:

```python
from pydantic import BaseModel


class Pirate(BaseModel):
    name: str
    gold: float
    crimes: list[str]
```

You've set up the type constraints using type hints. If you try to instantiate a Pirate model with the wrong type of
`crimes`:

```python
jack_sparrow = Pirate(name='Captain J.S.', gold=100.0, crimes='theft')
# instantiate a Pirate with `crimes` being a string, not list ^^^^^^^
```

the above will fail the data validation process, because the instantiated model will not meet the type constraints
you've set up in the model definition.

## Invalid model

What can cause a `ValidationError` when you're trying to instantiate a subclass of `BaseModel`?

One of the causes is **field validators**. We will cover this topic when the time comes.

Beyond field validators, there are two requirements already built into the `BaseModel` class which, when
violated, lead to a `ValidationError`:

1. all fields without a default value must be assigned a value
2. every model field must receive a value _compatible_ with its type hint

The first one is not specific to Pydantic, actually. Dataclasses will also raise an exception if you don't provide a
value for a reqiured (non-optional) field:

```python
from dataclasses import dataclass


@dataclass
class Gangster:
    warrants: list[str]
    is_armed: bool


killa = Gangster(warrants=['FBI', 'LAPD', 'NSA'])  # TypeError: missed a required positional argument `is_armed`
```

Though there is a slight difference - missing required fields are treated by Pydantic as _validation errors_, not
_type errors_.

Well, the first requirement was quite obvious, so let's take a closer look at the second one in the next lesson.

## Assignment

Open the `Questions` tab in the practice panel on the right and complete the quiz.
