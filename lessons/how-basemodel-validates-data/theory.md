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
we've set up in the model definition.

Or, if you remember the introduction to pydantic lesson, we could define a *field validator* in our model
to check, for example, if `crimes` is an empty list, and if so, raise a ValidationError. Can't be a law abiding pirate,
can you? So even if the *types* are correct, the *values*, which are subject to validation too, can be unacceptable.

## The exact reasons for validation errors

There are two ways you can get a validation error when trying to instantiate a subclass of `BaseModel`

One of them is field validators. They are defined by you and raise errors when an instance doesn't meet your custom
rules. We will cover this topic when the time comes.

Beyond field validators, there are two requirements already built into the `BaseModel` class which, when
violated, lead to a ValidationError:

1. missing required fields are treated by Pydantic as validation errors
2. every model field must receive a value _compatible_ with its type hint

The first one is not specific to Pydantic, actually. Dataclasses will also raise an exception if you don't provide a
value for a required field:

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

Let's take a closer look at the second requirement

## Forgivable type validation

"Every model field must receive a value _compatible_ with its type hint". The emphasis is on the word "compatible". 

Here's a little revelation: up to this moment i didn't mention that, but Pydantic handles not only data validation,
but also data _transformation_! 

