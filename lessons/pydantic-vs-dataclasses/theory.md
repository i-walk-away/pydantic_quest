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

Then our app calculates how old they will be next year.

You might recall what the path that this data takes looks like:

1. User sends `username` and `age`
2. We build a `UserFormDTO` out of this data
3. We call `calculate_age` function and pass the DTO as an argument to it
4. The age is calculated
5. The result is returned to the user

Now let's zoom in on what is actually happening here.

One part of our code receives raw, volatile data from the outside world. That data may be wrong, incomplete, malformed,
or just silly.

Another part of our code does the actual work (calculates `age + 1`)

People usually have names for these two parts:

- the part that receives input from the outside world is often called the **API layer** or **presentation layer**
- the part that does the actual work is often called the **business logic layer**

Imagine a wooden gate. There is a guard standing in front of it - sir API Layer. Behind the gate there is a big room
full of machines that do different things. There is an age calculating machine, username changing machine and a whole
lot of others. This room is the business logic layer.

So a man approaches the gate. This man - the user - wants to know his future, he has a special request: "what age will
i be next year?". So he writes his age and name on a piece of paper and hands it to sir API Layer. It is then the guards
responsibility to make sure that the submitted data is valid, before he then goes into the business logic layer and
feeds the data into the age calculating machine. The output is then received by the guard and handed to the user.

The busiess logic layer is nothing but a collection of functions that can do different things. And the presentation
layer is just a user-facing interface that accepts requests and knows which functions to call to achieve what the user
wants.
They have their own respective responsibilities. For example, we established in the previous lesson that data validation
is better handled *before* it reaches the actual machines.

In an ideal world, these two layers are so isolated from each other that, as long as the _contract_ between them remains
unchanged, one layer can be heavily rewritten without forcing ANY changes in the other. Here, _contract_ means the agreed
shape of the input and output between the two layers: what fields the input DTO have, and what data is returned.

## The tempting mistake

So we know that Pydantic is great at validating data, and our business logic layer expects the inputs to be
already validated. It's tempting to do this:

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

We validate data with Pydantic, and then our actual function expects an object that inherits from BaseModel, which
is guaranteed to contain valid data.

So what is the problem?

## Consequences

The problem is not that this code immediately explodes. In fact, it may work perfectly well for quite a while.

The real problem is _architectural_.

Our function that calculates the age is part of the business logic layer of the app. Its job is to just calculate the
age. The only thing that matters to a function in the business logic layer, is that the input data is valid, without
having a slightest clue about _how_ that validation is enforced.

But we made that function depend on a DTO which inherits from Pydantic `BaseModel`.
That means Pydantic - a library we introduced mainly to validate unsanitized data from the outside world - has now
become a dependency of the business logic layer too.

In other words, the validation library has leaked further into the codebase than it really needed to.
This is what people mean when they say **leaked dependency**.

## Why this matters

Let's imagine that after some time, a brand new API framework gets released - **GangstAPI** - with built-in support for
**msgspec**, which is faster and more lightweight than Pydantic for your use case.

Now you want to migrate.

In an ideal world, this would only affect the outer part of your app - the part that receives and validates user input.
You would switch frameworks, switch validation libraries, and keep the actual business functions intact, since, once
again, they don't care about the implementation details of the API layer. The only "agreement" it should have with
the API layer is that the data will be valid.

But you can't do that cleanly anymore.

Why?

Because your business logic is expecting _exactly_ Pydantic models. So now you have to go through the code and make sure
you are not:

- expecting `BaseModel` subclasses everywhere
- relying on Pydantic-specific behavior
- using Basemodel-specific methods, which your new msgspec library simply doesn't have or they work differently

That is the consequence of the leak.
A library that should have stayed near the boundary of the app has become part of the deeper logic too.

## What should happen instead

The safer approach is this:

1. We receive raw input from the outside world
2. We validate it with the library of our choice - for example, Pydantic
3. Once the data is confirmed to be valid, we build a plain dataclass out of it
4. We pass that plain dataclass to the actual business functions

That way, the function that does the real work does not care how the data was validated.
It only cares that the data is already valid.

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

This is much cleaner.

The validation library does its job at the API layer where raw input enters the app.
After that, your inner code works with plain Python data structures.

## Why dataclasses are good for this

A pure dataclass is boring - and that is exactly the point.

It does not carry the behavior of some third-party validation library.
It does not tie your business code to `BaseModel`.
It is just a plain container for already validated data.

That makes it a good choice for the parts of your code that should stay simple and isolated.

So the difference is not really:

> Pydantic good, dataclasses bad

The real difference is closer to this:

- Pydantic is great for validating volatile input coming from the outside world
- dataclasses are great for carrying already validated data through the rest of your code

## Conclusion

When should you use Pydantic models and when should you use dataclasses?

1. Use Pydantic when you are dealing with raw, unsanitized data from the outside world.
2. Once that data is validated, map it into a pure dataclass.
3. Let the rest of your code work with the dataclass instead of depending on the validation library.

That way, your validation library stays where it belongs, and your actual business functions do not care how the data was
validated in the first place.
