## What should happen instead

Our leaking data validation flow looks like this:

1. We receive raw input from the outside world
2. We validate it by constructing a subclass of `BaseModel` out of this data
3. Once the data is confirmed to be valid, it is passed to the **business logic layer**

There is a simple way to prevent that by adding an additional step:

1. We receive raw input from the outside world
2. We validate it with the library of our choice - Pydantic, msgspec, self-written library, whatever
3. Once the data is confirmed to be valid, we build a _dataclass_ out of it
4. We pass that plain dataclass to the actual business functions

That way, the function that does the real work does not care how the data was validated. It only cares that the data is
already valid.

For example, we might validate with Pydantic first:

```python
from pydantic import BaseModel


class UserFormRequest(BaseModel):
    name: str
    age: int
```

and then map the validated data into a pure dataclass:

```python
from dataclasses import dataclass


@dataclass
class UserFormDTO:
    name: str
    age: int
```

Then the actual function works with the dataclass:

```python
def calculate_age_next_year(data: UserFormDTO) -> int:
    return data.age + 1
```

This is much cleaner!

Remember: after the data is validated, the validation library's job is *done*. It shouldn't leak beyond the boundaries
of the **API layer**.

## Why dataclasses are good for this

A pure dataclass is shipped in python's standard library.

It does not carry the behavior of some third-party validation library, and it does not tie your business code to
`BaseModel`. It is just a plain container for data.

That makes it a good choice for the parts of your code that should stay simple and isolated.

- Pydantic is great for validating volatile input coming from the outside world
- dataclasses are great for carrying already validated data through the rest of your code

## Conclusion

When should you use Pydantic models and when should you use dataclasses?

1. Use Pydantic when you are dealing with raw, unsanitized data from the outside world
2. Once that data is validated, map it into a pure dataclass
3. Let the rest of your code work with the dataclass instead of depending on the validation library

That way, your validation library stays where it belongs, and your actual business functions stay completely isolated
from the implementation details of the **API layer**.

## Assignment

Open the `Questions` tab in the practice panel on the right and complete the quiz.
