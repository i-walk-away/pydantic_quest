## The ultimate dataclass

After the previous lesson, you might have gotten an impression that Pydantic models are just better dataclasses. Easier
strict typing, powerful validators, de/serialization support - and they both generally serve the same purpose: to carry
data between parts of your application.

But Pydantic is not just an ultimate dataclass. In a real project, Pydantic models _complement_ dataclasses, not replace
them.

What exactly are their respective use cases?

## Where Pydantic belongs

Let's continue using the same website example from the previous lesson.
The user enters two values:

```text
Enter your username: ...
Enter your age: ...
```

Then our app uses this data to calculate how old they will be next year.

You might recall the path that this data takes through our application:

1. User sends `username` and `age`
2. We build a `UserFormDTO` out of this data
3. We call `calculate_age` function and pass the DTO as an argument to it
4. The age is calculated
5. The result is returned to the user

Now let's zoom in on what is actually happening here.

One part of our code receives raw, volatile data from the outside world. That data may be wrong, incomplete, malformed,
or just silly.

Another part of our code does the actual work (calculates `age + 1`)

Smart people from the software architecture field had came up with names for these two parts:

- the part that receives input from the outside world is often called the **API layer** or **presentation layer**
- the part that does the actual work is often called the **business logic layer**

An analogy will make the separation of concerns easier to understand.

Imagine a wooden gate. There is a guard standing in front of it - **Sir API Layer**. Behind the gate, there is a big room
full of machines that do different things. There is an age calculating machine, username changing machine and a whole lot
of others. This room is the **business logic layer**.

So a man approaches the gate with a request: "what age will i be next year?". He writes
down his age and name on a piece of paper and hands it to **Sir API Layer**. It is then the _guards_
responsibility to make sure that the data is valid before he goes into the **business logic layer** and
feeds the data into the age calculating machine. The output is then received by the guard and handed out to the user.

The busiess logic layer is nothing but a collection of functions that do different things. The presentation layer is
just a user-facing interface that accepts requests and knows which functions to call.

They have their own respective responsibilities. For example, as we established in the previous lesson, data validation
is better handled *before* it reaches the actual machines - in the **API layer**.

In an ideal world, these two layers are so isolated from each other that, as long as the _contract_ between them remains
unchanged, one layer can be _heavily_ rewritten without forcing ANY changes in the other. Here, _contract_ means the
agreed shape of the input and output between the two layers: what fields the input DTOs have, and what data is returned.

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
which inherits from Pydantic's `BaseModel` class. That means Pydantic - the **API layer**'s dependency - has now become
a
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

Because you made your business logic functionsexpect _exactly_ Pydantic models. So now you have to go through the code
and make sure you are not:

- expecting `BaseModel` subclasses everywhere
- relying on Pydantic-specific behavior
- using Basemodel-specific methods, which your new msgspec library simply doesn't have or they work differently

As you sow, so shall you reap!
A library that should have stayed near the boundary of the app (the API) has become part of the deeper logic too.

## What should happen instead

Our leaking data validation flow looks like this:

1. We receive raw input from the outside world
2. We validate it by constructing a subclass of `BaseModel` out of this data
3. Once the data is confirmed to be valid, it is passed to the **business logic layer**

There is a simple way to prevent that by adding an additonal step:

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
