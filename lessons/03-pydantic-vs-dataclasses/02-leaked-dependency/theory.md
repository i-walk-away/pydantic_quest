## The tempting mistake

So we know that:

1. Pydantic is great at validating data
2. our **business logic layer** expects the inputs to be already validated

It's therefore tempting to do the following:

```python
def calculate_age_next_year(data: UserFormDTO) -> int:
    return data.age + 1
```

and then define the DTO like this:

```python
from pydantic import BaseModel


class UserFormDTO(BaseModel):
    name: str
    age: int
```

As you can see here, our actual function expects an object that inherits from `BaseModel`. This is rather convenient.
By expecting a model that wouldn't even initialize if the data was invalid, we ensure the integrity of the input data
and let our **business logic layer** stick to its only job: modifying or calculating stuff.

Why is it a mistake then?

## Consequences

The problem is not that this code immediately explodes. In fact, it may work perfectly well for quite a while.

The real problem is _architectural_.

Our function that calculates the age is part of the **business logic layer**. Its sole job is to just calculate the age.
The only thing that matters to a function in the **business logic layer** is that the input data is valid, without having
the slightest clue about _how_ that validation is enforced.

The layer that **does** cate about the data validation is the **API layer**.

Which means that Pydantic is a dependency of the _API layer_. But we made our business logic function depend on a DTO
which inherits from Pydantic's `BaseModel` class. That means Pydantic - the **API layer**'s dependency - has now become a
dependency of the **business logic layer** too.

In other words, the validation library has _leaked_ further into another layer.
You are now a victim of a **leaked dependency**.

## Why this matters

After some time, a brand new API framework gets released - **GangstAPI** - with built-in support for
**msgspec** data validation library, which turns out to be faster and more lightweight for your use case.

Now you want to migrate.

In an ideal world, this would only affect the outer part of your app - the part that receives and validates user input.
You would switch frameworks, switch validation libraries, and keep the actual business functions intact. The only
"agreement" they should have with the **API layer** is that the DTOs will be valid and have the same fields.

And then you realize that the migration is going to affect a lot more code than you expected. Why?

Because you made your business logic functions expect _exactly_ Pydantic models. So now you have to go through the code
and make sure you are not:

- expecting `BaseModel` subclasses everywhere
- relying on Pydantic-specific behavior
- using BaseModel-specific methods, which your new msgspec library simply doesn't have or they work differently

As you sow, so shall you reap!
A library that should have stayed near the boundary of the app (the API) has become part of the deeper logic too.

## Assignment

Open the `Questions` tab in the practice panel on the right and complete the quiz.
