## Pydantic models

Now that you've learned _why_ you should use Pydantic, let's break down _how_ to use it.

To define a Pydantic model, you must import `BaseModel` and inherit from it:

```python
from pydantic import BaseModel


class Gangster(BaseModel):
    name: str
    crime_count: int
    is_original: bool
```

All the internal type validation is handled by the `BaseModel`. You only need to provide type hints for class attributes.
Then Pydantic automatically makes sure that the data used to construct a subclass of `BaseModel` satisfies your
type hints:

```python
from pydantic import BaseModel


class Gangster(BaseModel):
    crime_count: int
    is_original: bool


carl_johnson = Gangster(crime_count=904, is_original=True)  # works
valera_kotakbas = Gangster(crime_count=2, is_original='yeah')
# ValidationError: `is_original` must be of type bool ^^^^^^ as per your type hint. passed string instead
```

## Assignment

Define a Pydantic model `Pirate` with the following fields:

1. name (must be a string)
2. gold (must be a float)
3. crimes (must be a list of strings)

