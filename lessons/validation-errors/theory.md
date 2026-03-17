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

There are two ways you can get a validation error when trying to instantiate a subclass of `BaseModel`

One of them is field validators. They are defined by you and raise errors when an instance doesn't meet your custom
rules. We will cover this topic when the time comes, but if you remember the 'introduction to pydantic' lesson, you've
seen that you can define a *field validator* in your model
to check, for example, if `crimes` is an empty list, and if so, raise a ValidationError manually.
Can't be a law abiding pirate,
can you? So even if the *types* are correct, the *values*, which are subject to validation too, can be unacceptable
and lead to a validation error.

Beyond field validators, there are requirements already built into the `BaseModel` class which, when
violated, lead to a ValidationError:

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

Well, the first requirement was quite obvious, so let's take a closer look at the second one.

## Forgivable type validation

"Every model field must receive a value _compatible_ with its type hint". The emphasis is on the word "compatible".

Here's a little revelation: up to this moment i didn't mention that, but Pydantic handles not only data validation,
but also data _transformation_!

For a while i've been lying to you that Pydantic will enforce strict typing, but the truth is that by default, Pydantic
will try to _transform_ a value of an invalid type to a valid one instead of just falling with an error.

Here is an example:

```python
from pydantic import BaseModel


class Pirate(BaseModel):
    gold: float


sparrow = Pirate(gold=100)  # an integer, not a float! 
print(sparrow.gold)  # 100.0  <--  transformed to a float for us

blackbeard = Pirate(gold='5000.0')
print(blackbeard.gold)  # 5000.0  <--  string numbers are transformed too
```

Pydantic knows that we expect a float here. And if the input data makes sense, even though its *type* is invalid, it
lends us a hand and converts this data to the expected type instead of rasing an exception.

Strings that consist of numeric characters are _compatible_ with `int` and `float` type hints. Integets and floats are
_compatible_ with each other's type hints.

A less obvious example:

```python
from pydantic import BaseModel


class Gangster(BaseModel):
    is_armed: bool


killa = Gangster(is_armed='True')
print(killa.is_armed)  # True  <--  transformed to a bool
```

### Discovery

Here is a funny one! When i was writing the previous lesson about BaseModels, i wanted to show how it fails with a
validation error if you try to instantiate a subclass with the wrong field types:

```py
from pydantic import BaseModel


class Gangster(BaseModel):
    crime_count: int
    is_original: bool


big_smoke = Gangster(crime_count=200, is_original='Yes')  # i assumed there would be a validation error here
```

I thought it would be a hilarious way to get a validation error, by passing just "yes" instead of a boolean.

But when i tried to actually run this code... It didn't fail!

```python
print(big_smoke)  # crime_count=200 is_original=True
```

Pydantic literally transforms `"Yes"` to `True` and `"No"` to `False` for you :)

And before you test it: no, Pydantic only speaks english. `'Si'`, `'Oui'` and `'Да'` strings didn't get transformed
to a boolean. 