## What is Pydantic

Pydantic is the most widely used data validation library for Python.
Around 8,000 packages on PyPI use Pydantic under the hood, including massively popular
libraries like FastAPI, huggingface, and LangChain.

What problems does it solve?

## Why use Pydantic

Python is a dynamically typed language. It means that the *type* of the objects (variables, functions)
can change throughout the object's lifecycle:

```python
var = 12
var = "string"  # <-- statically typed languages would execute you on spot for this
```

To be precise, it's not that the type of a variable changes - it's that in python, variables themselves don't have a
type *at all*.

```python
var = 12  # var references an integer object. it POINTS to an int object
var = "string"  # var now references a string object
```

In statically typed languages like Java this woudln't work:

```java
int x = 12;   // x is declared as integer
x = "hello";  // compile error - x can only hold integers
```

Dynamic typing has _some_ benefits to it, but we will focus solely on the downsides (you generally should not do that in
life)

### Consequences

The main downside is that wrong data often survives longer than it should.

For example:

```python
def calculate_age_next_year(age):
    return age + 1


calculate_age_next_year("18")  # we passed a string here
```

This code crashes only when `+ 1` is attempted.
The function did not reject the value and attempted to work with it, even though the value was wrong for the job.

That is bad:

- Python lets values move through the program very freely
- mistakes are often discovered late
- the error may happen far away from where the bad data first entered the system
- also ABSOLUTELY UNREADABLE code

That makes debugging harder, especially in larger applications.

### But what about type hints?

Since Python 3.5, we can add *hints* about our variables' types:

```python
x: int = 78  # x should be an integer
things: list[str] = ["stuff", "entities"]  # things should be a list of strings
```

This helps a lot.

1. The code is now readable.
2. Good people will create static type checkers and other good people will add IDE support for them, allowing you to
   see warnings and errors as you code.
3. IDEs can offer better autocomplete and navigation

For example, a static type checker would complain about this:

```python
def calculate_age_next_year(age: int):
    return age + 1


calculate_age_next_year("18")  # <-- warning: Expected type 'int', got 'str' instead
```

But they're called type *hints* for a reason. You can STILL go Rambo and do this:

```python
x: int = 78
x = "Rambo"
```

This is a valid python program that will not refuse to run. Correct typing is NOT enforced at runtime.

### Data validation

Imagine you have a website that calculates how old you will be when you're 1 year older. This may not be the most
useful website, but it gives us something to work with.

The user is prompted to fill in this data:

```text
Enter your username: ...
Enter your age: ...
```

The user submits this data, your backend receives it, and then your code uses it.
A simplified path looks like this:

1. API layer receives `username` and `age` from the user
2. business logic uses that data (calculates age + 1)
3. the result is returned to the user

Now imagine your business logic expects a small object like this:

```python
@dataclass
class UserFormDTO:
    username: str
    age: int
```

A DTO, or *Data Transfer Object*, is just a small object whose job is to carry structured data
from one part of the program to another. Data submitted by the user gets gathered into a single UserFormDTO object, with
its `username` and `age` values being whatever was submitted by the user.

So when a user sends:

```python
{"username": "Adolf", "age": 20}
```

we have a UserFormDTO object with `username`="Adolf" and `age`=20 and we can use this object in our business layer.

Then your actual business logic may look like this:

```python
def calculate_age(data: UserFormDTO) -> str:
    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

We can now see a less simplified path of our data:

1. User sends `username` and `age` to our API
2. API layer builds a `UserFormDTO` out of this data
3. API layer calls `calculate_age` and passes the DTO as an argument to it
4. The age is calculated
5. the result is returned to the user

However this system assumes two things are true:

- `username` is actually a string
- `age` is actually an integer

But what if the incoming data looks like this?

```python
{"username": "Alice", "age": "Albania"}
```

The user was a little bit silly and sent us 'Albania' as their age. This is clearly not an integer. So the data was
broken from the very beginning. When _exactly_ will our program fail?

1. User sends `username: "Alice"` and `age: "Albania"` to our API -- ✓
2. API layer builds a UserFormDTO out of this data -- ✓
3. API layer calls `calculate_age` and passes the DTO as an argument to it --- ✓
4. The age is calculated <-------- *runtime error upon trying to add 1 to a string*
5. ...

The broken data made quite a long jorney through our program before something. It shouldn't have even **reached** the
business logic layer and instead should've been rejected by the API layer on step 2, becuase the data was broken:

1. User sends `username: "Alice"` and `age: "Albania"` to our API -- ✓
2. API layer builds a UserFormDTO out of this data <----- *Validation error: couldn't assign `{age: Albania}` to
   `UserFormDTO.age`, because UserFormDTO expects age to be an integer and user sent string instead*

Statically typed language like Java would fail with a runtime error on step 2. But Python allows that.

There are some ways to work around this issue. Let's start by simply modifying our business logic to check if the passed
values are of correct types:

```python
def calculate_age(data: UserFormDTO) -> str | None:
    if not isinstance(data.age, int):
        return None

    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

This doesn't look like much improvement, since our broken data still makes it to our business logic layer. However
imagine if our function performed some expensive operations on this data instead of a simple addition:

```python
def calculate_age(data: UserFormDTO) -> str | None:
    if not isinstance(data.age, int):
        return None

    ages = very_large_database_of_ages.get_average_age()  # expensive DB operation

    response = f"{data.username} will be {data.age + 1} years old next year! The average age is {ages}."
    return response
```

Then we actually want our function to fail before it does this expensive operation to not waste time and resources on
something that will fail anyway.

Did we solve our problem? Well... Kinda. The code didn't get much uglier while still meeting our requirement of failing
before an expensive operation. But this solution doesn't scale very well. What if we need multiple checks? And if they
are not as simple?

Example below is *a little bit* exaggerated, but it does show the problem with scaling.

```python
def find_old_people(data: list[UserFormDTO]) -> list[str] | None:
    """
    Find old people in a list of UserFormDTO and return their usernames
    """
    if not isinstance(data, list):
        return None

    for i, dto in enumerate(data):
        # check if it's actually a UserFormDTO (or at least has the right attrs)
        if not hasattr(dto, 'username') or not hasattr(dto, 'age'):
            return None

        # check username is string and not empty
        if not isinstance(dto.username, str) or len(dto.username.strip()) == 0:
            return None

        # check age is integer and within reasonable range
        if not isinstance(dto.age, int):
            return None
        if dto.age < 0 or dto.age > 150:
            return None

        # check for None values
        if dto.username is None or dto.age is None:
            return None

    # now that validation is done, we can do the actual business logic
    old_people: list[str] = []

    for man in data:
        if man.age > 70:
            old_people.append(man.username)

    return old_people
```

That's a lot of checks! And a bunch of problems too:

1. We will often have to reimplement the same checks for different business logic functions
2. Data validation itself is *beyond the scope* of business logic layer. This is a violation of the Single Responsibility
   Principle. The data has to be validated before it reaches business logic layer.


It looks like validating data in our function doesn't cut it. There is a better way though - and it's to implement data
validation in our *model istelf* - in `UserFormDTO` class. 