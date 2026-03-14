## The ultimate dataclass

After the previous lesson, you might have gotten the impression that Pydantic models are just better dataclasses. Easier
to enforce strict typing, powerful validator syntax, de/serialization support - and they both serve generally the same
purpose: to carry data between parts of your application.

But Pydantic is not just an ultimate dataclass. In a real project, Pydantic models _complement_ dataclasses, not replace
them.

What exactly are their respective use cases? And is there a difference in performance?

## Software layers

Let's step back a little and expand our website example from the previous lesson.

In software architecture, a _layer_ is just a part of the application with a specific responsibility.
We divide the code into chunks that each have their own job.

For example:

- one part receives data from the user
- one part performs the actual calculations and applies rules
- one part talks to the database

Those parts are called **layers**.

The age calculating website's code can be imagined as a system that consists of 3 **layers**:

1. Presentation layer
2. Business logic layer
3. Repository layer

The _presentation_ layer is basically what the end user sees - the API (hence the reason i will oftern refer to it as
an "API layer"). It's where the user data is sent.
Its job is to receive input and return output. It is _not_ where the "age + 1" is calculated.

Afterwards comes the _business logic layer_. It's just a set of functions that
sit there, waiting to be used to apply business rules (like adding +1 to someone's age). So when the user sends some data
to our application, the API - which is our presentation layer - calls the appropriate methods of the business logic layer
and passes user data to them.

The _repository_ is a layer that handles database operations (although i simplified it a little). Whenever a function in
the business layer needs a connection to the database to create / read / update / delete an entity, it can
access the database through the repository layer. The repository itself just provides simple public methods like `add()`
and `get_by_id()`, while the implementation is abstracted inside it. We will omit this one, as it is beyond the scope
of the current lesson.

A horizontal representation of the three layers makes more sense:

```
presentation <-> business logic <-> repository
```

You might recall from the previous lesson the path that data moves through in our website:

1. User sends `username` and `age`
2. we build a `UserFormDTO` out of this data
3. we call `calculate_age` and pass the DTO as an argument to it
4. The age is calculated
5. the result is returned to the user

Now let's rewrite it using the newly learned layer terminology:

1. User sends data to our presentation layer - the website API
2. The presentation layer uses this data to construct a DTO
3. The presentation layer calls a function from the business logic layer, like `calculate_age(data: UserFormDTO)`, and
   passes this DTO as an argument to it
4. The business logic layer evaluates the function and returns the result to the presentation layer
5. The presentation layer sends the response back to the user


So the presentation layer deals dorectly with raw user input. The business logic layer should ideally just receive
clean data and do its job.

And let's make a mistake here. We know that Pydantic is so great that it almost guarantees data integrity without much
effort from our side. Let's make all the business layer functions expect Pydantic-based DTOs as input data!

```python
def calculate_age(data: UserFormDTO) -> str:
    """
    Apply le business rule
    """
    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

And the DTO inherits from BaseModel:

```python
from pydantic import BaseModel


class UserFormDTO(BaseModel):
    username: str
    age: int
```

This certainly makes our life easier. The API builds Pydantic models out of user data, ensuring its validity, and the
business
logic layer just expects instances of those models as input, so it can only work with valid data.

### Consequences

Then our website got bigger and bigger, age calculations became more complex, and after a while a new data API framework
just dropped - **GangstAPI**, with built-in support for the **msgspec** data validation library, which is faster and more
lightweight!

We now want to migrate the API layer to GangstAPI framework. Thankfully, since our application is divided into layers,
we should be able to modify the presentation layer without having to change anything else. It doesn't matter how
the presentation layer works exactly, as long as the data sent to the logic layer is valid, since the business logic
is isolated from the implementation details of other app layers.

Or is it?

Uh-oh. But the `calculate_age()` function, as well as everything else in the business logic layer, expects the input data
to inherit from Pydantic BaseModel! Suddenly we discover a flaw in our software architecture - a **leaked dependency**.

// note to self: in the given example this did not break anything because no basemodel-specific methods were used. no
runtime errors will occur in the business logic layer simply because the input data inhetits from something other than
pydantic basemodel as long as the field names don't change and no basemodel methods are called in the function body. fix
later

## Clean architecture

As we established in the previous lesson, data validation is a responsibility of the API layer. We want our business
logic to safely assume that all inputs are valid by definition and ensure the validity itself elsewhere.

It means that whatever data validation library we use, it's a dependency of the *API layer*. All layers of our
website should ideally be CLUELESS about the implementation details of the other layers. But we've made a mistake
and have *leaked* an API layer dependency into our business logic, coupling together what should be isolated.

For large scale applications, a leaked dependency might mean additional weeks of labor to migrate to a new library.

How can we achieve such isolation?

## Business logic layer should work with pure dataclasses

A simple solution is to make sure that our presentation layer emits simple dataclasses, not BaseModels or other
third-party models. Business logic then should expect dataclasses as inputs and return dataclasses too.

1. User sends some data
2. API layer validates it by trying to construct a Pydantic model out of it
3. If data is confirmed to be valid, construct a simple dataclass with the same field names and values
4. Pass the clean dataclass as an argument to a function in the business logic layer

Such an approach allows us to change API frameworks and data validation libraries without having to even touch the other
layers of the application, as per the Encapsulation principle of Object Oriented Programming.

Pydantic, msgspec, a self-made library - it doesn't matter, as long as regular dataclasses are built from the validated
data before being sent as inputs to the business logic layer, ensuring its isolation from the implementation details of
the other parts of the codebase.

## Conclusion

When to use Pydantic models and when to use dataclasses?

1. Use Pydantic to make sure that the wild data of unknown integrity is validated before crossing the API layer.
2. Since data is now valid, convert the Pydantic model into a pure dataclass to protect other layers from a leaked
   dependency.
3. Send pure dataclasses to the business logic layer.

The above can be extrapolated to any data validation library. After the data is confirmed to be ok, its job is done.
There is nothing but harm in leaking it further into your application! 
