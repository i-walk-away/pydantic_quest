## Forgivable type validation

Every model field must receive a value _compatible_ with its type hint. The emphasis is on the word "compatible".

Here's a little revelation: up to this moment i didn't mention that, but Pydantic handles not only data validation,
but also data _transformation_!

For a while i've been lying to you, saying that Pydantic will enforce _strict_ typing. The truth is that by default,
instead of just falling with an error, Pydantic will try to **transform** a value of an invalid type to a valid one.

Here is an example:

```python
from pydantic import BaseModel


class Pirate(BaseModel):
    gold: float                     #  <--  we expect a float value of `gold`


sparrow = Pirate(gold=100)          # an integer, not a float! 
print(sparrow.gold)                 # 100.0  <--  transformed to a float for us

blackbeard = Pirate(gold='5000.0')
print(blackbeard.gold)              # 5000.0  <--  string numbers are transformed too
```

Pydantic knows that we expect a float here. And if the input data makes sense, even though its *type* is invalid, it
lends us a hand and converts this data to the expected type instead of rasing an exception.

This is _type coercion_.

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

Here is a funny one! When i was writing the lesson about BaseModels, i wanted to show how it fails with a
validation error if you try to instantiate a subclass with the wrong field types. Here was my example code:

```py
from pydantic import BaseModel


class Gangster(BaseModel):
    crime_count: int
    is_original: bool


big_smoke = Gangster(crime_count=200, is_original='Yes')  
# i assumed there would be a validation error     ^^^^^
```

I thought it would be a hilarious way to get a validation error, by passing just "Yes" instead of a boolean.

But when i tried to actually run this code... It didn't fail!

```python
print(big_smoke)  # crime_count=200 is_original=True
```

Pydantic literally transforms `"Yes"` to `True` and `"No"` to `False` for you :)

And before you test it: no, Pydantic only speaks english. `'Si'`, `'Oui'` and `'Да'` strings didn't get transformed
to a boolean. 

// add link to all compatible types later