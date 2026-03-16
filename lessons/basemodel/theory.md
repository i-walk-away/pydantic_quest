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

All the internal type validation is handled by the `BaseModel`. You only need to provide type hints for class attributes,
and then Pydantic automatically makes sure that the data used to construct a subclass of `BaseModel` satisfies your 
type hints:

```python
from pydantic import BaseModel


class Gangster(BaseModel):
    crime_count: int
    is_original: bool


carl_johnson = Gangster(crime_count=904, is_original=True)  # works
valera_kotakbas = Gangster(crime_count=2, is_original='yeah')
# ValidationError: `is_original` must be of type bool ^^^^^^
```

