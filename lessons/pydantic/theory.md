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


calculate_age_next_year("18")  # ValueError: we passed a string here, can't add +1 to a str
```

This code crashes only when `+ 1` is attempted.
The function did not reject the value and attempted to work with it, even though the value was wrong for the job.

That is not very convenient. Python lets values move through the program very freely, and the errors may happen far away
from where the bad data first entered the system. Also untyped code is *absolutely*
unreadable.

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

1. API layer of our website receives `username` and `age` from the user
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

we build a UserFormDTO object out of it, with `username`="Adolf" and `age`=20, and we can use this object in our business
layer.

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

The broken data made quite a long jorney through our program before something exploded. It shouldn't have even
**reached** the business logic layer and instead should've been rejected by the API layer on step 2, becuase the data was
broken:

1. User sends `username: "Alice"` and `age: "Albania"` to our API -- ✓
2. API layer builds a UserFormDTO out of this data <----- *Validation error: couldn't assign `"Albania"` to
   `UserFormDTO.age`, because UserFormDTO expects age to be an integer and user sent string instead*

Statically typed language like Java would fail with a runtime error on step 2. But Python allows that.

### Validating data in the business logic layer

There are some ways to work around this issue. Let's start by simply modifying our business logic to check if the passed
values are of correct types:

```python
def calculate_age(data: UserFormDTO) -> str:
    if not isinstance(data.age, int):  # check if data.age is not an instance of class 'int'
        raise TypeError(f'{data.age} is not an integer!')  # if so, exit early with an error 

    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

Although broken data still makes it into our business logic layer, this small check prevents our function from wasting
time on trying to perform operations on an invalid input data. Well, in our simple example, the difference between
exiting early and crashing on `age + 1` is negligible. However imagine if our function performed some expensive
operations on this data instead of a simple integer addition:

```python
def calculate_age(data: UserFormDTO) -> str | None:
    if not isinstance(data.age, int):
        raise TypeError(f'{data.age} is not an integer!')

    ages = very_large_database_of_ages.get_average_age()  # expensive DB operation

    response = f"{data.username} will be {data.age + 1} years old next year! The average age is {ages}."
    return response
```

Then we actually want our function to fail before it does this expensive operation. Why waste time and resources on
something that is doomed to fail anyway?

But did our little `isinstance()` check solve the problem? Well... Kind of. The code now meets our requirement of failing
before an expensive operation. But this solution doesn't **scale** very well. What if we needed multiple checks? And if
they were not as simple?

Example below is *a little bit* exaggerated, but it does show the problem with scaling. // note to self: raise exceptions instead of returning none

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

1. We will likely have to reimplement the same checks for different functions inside business logic layer (violates
   _DRY_ - Don't Repeat Yourself principle)
2. Instead of only doing its job - finding old people in a list - our `find_old_people()` function also handles complex
   data validation (violates _SRP_ - Single Responsibility Principle)
3. Data validation itself is *beyond the scope* of business logic layer. It's not business layer's responsibility to
   check if the data was valid (violates the principles of clean architecture)

Looks like validating data inside the function doesn't cut it. There is a better way though - and it's to implement data
validation in our *model istelf* - in the `UserFormDTO` class.

### Validating data in the model class

Let's modify our user form model class by adding some validation logic to it:

```python
from dataclasses import dataclass


@dataclass
class UserFormDTO:
    username: str
    age: int

    def __post_init__(self):
        """
        Post init is called after the dataclass initializes
        """
        self._validate_type(self.username, str, "username")
        self._validate_type(self.age, int, "age")

    @staticmethod
    def _validate_type(value, expected_type, field_name):
        """
        Helper method to validate a single value
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name} must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
```

If we now try to instantiate a `UserFormDTO` with invalid data, a `TypeError` will be thrown:

```python
try:
    user = UserFormDTO(username="Alice", age="30")  # invalid age type
except TypeError as e:
    print(f"Error: {e}")
```

```expected
TypeError: age must be int, got str
```

Now our business function no longer has to care about the validity of the input data, becuase our Data Transfer Object
itself handles validation at *class level*:

```python
def calculate_age(data: UserFormDTO) -> str:
    """
    The validity of `data` is confirmed before it even reached our business logic
    """
    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

This approach is significantly better.

1. Business logic layer can always safely assume that it will receive valid data and doesn't have to check it itself
2. All validation logic is isolated within our model
3. Invalid data is rejected at the earliest possible moment (unless you're holding the user at gunpoint, preventing them
   from even _submitting_ broken data)
4. We can add more complex validation logic to our model without changing anything else

On top of basic type validation, we can also validate some business rules too:

```python
from dataclasses import dataclass


@dataclass
class UserFormDTO:
    username: str
    age: int

    def __post_init__(self):
        """
        Post init is called after the dataclass initializes
        """
        # type validation
        self._validate_type(self.username, str, "username")
        self._validate_type(self.age, int, "age")

        # business rule validation
        self._validate_business_rules()

    @staticmethod
    def _validate_type(value, expected_type, field_name):
        """
        Helper method to validate a single value
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name} must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    def _validate_business_rules(self):
        """
        Validate all business rules
        """
        # age rules
        if self.age < 0:
            raise ValueError(f"age cannot be negative, got {self.age}")

        if self.age > 150:
            raise ValueError(f"prohibited from being older than 150, got {self.age}")

        # username rules
        if len(self.username) < 3:
            raise ValueError(f"username must be at least 3 characters, got {len(self.username)}")
```

Invalid types raise `TypeError` and invalid values raise `ValueError` and all of this happens in our API layer.
Oh, and we just invented **Pydantic**!

## Pydantic models

The problem that Pydantic was designed to solve is the lack of enforced type validation at runtime. Remember our
`UserFormDTO` implementation with _type_ validators?

```python
from dataclasses import dataclass


@dataclass
class UserFormDTO:
    username: str
    age: int

    def __post_init__(self):
        """
        Post init is called after the dataclass initializes
        """
        self._validate_type(self.username, str, "username")
        self._validate_type(self.age, int, "age")

    @staticmethod
    def _validate_type(value, expected_type, field_name):
        """
        Helper method to validate a single value
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name} must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
```

This is how you do it with Pydantic:

```python
from pydantic import BaseModel


class UserFormDTO(BaseModel):
    username: str
    age: int
```

That's it. `BaseModel` is a base class from which our models must inherit. `BaseModel` handles strict type validation
under the hood, and it knows which types our class attributes should be from our *type hints!*

If we tried this now:

```python
user = UserFormDTO(username="Alice", age="Albania")
```

We would get:

```
pydantic.error_wrappers.ValidationError: 1 validation error for UserFormDTO
age
  value is not a valid integer (type=type_error.integer)
```

Pydantic sees the `int` type hint of our `age` field and throws a `ValidationError` at us for trying to instantiate a
`UserFormDTO` with a wrong type. Our type *hints* now become type *requirements* with no extra syntax.

### Validators

We can also create simple methods for validating the actual values of our class attributes to enforce business rules.

Flashback to our implementation:

```python
from dataclasses import dataclass


@dataclass
class UserFormDTO:
    username: str
    age: int

    def __post_init__(self):
        """
        Post init is called after the dataclass initializes
        """
        # type validation
        self._validate_type(self.username, str, "username")
        self._validate_type(self.age, int, "age")

        # business rule validation
        self._validate_business_rules()

    @staticmethod
    def _validate_type(value, expected_type, field_name):
        """
        Helper method to validate a single value
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name} must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    def _validate_business_rules(self):
        """
        Validate all business rules
        """
        # age rules
        if self.age < 0:
            raise ValueError(f"age cannot be negative, got {self.age}")

        if self.age > 150:
            raise ValueError(f"prohibited from being older than 150, got {self.age}")

        # username rules
        if len(self.username) < 3:
            raise ValueError(f"username must be at least 3 characters, got {len(self.username)}")
```

Rewritten with Pydantic:

```python
from pydantic import BaseModel, field_validator


class UserFormDTO(BaseModel):
    username: str
    age: int

    @field_validator('age')
    @classmethod
    def validate_age(cls, value: int) -> int:
        """
        Validate age business rules
        """
        if value < 0:
            raise ValueError(f"age cannot be negative, got {value}")

        if value > 150:
            raise ValueError(f"prohibited from being older than 150, got {value}")

        return value

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        """
        Validate username business rules
        """
        if len(value) < 3:
            raise ValueError(f"username must be at least 3 characters, got {len(value)}")

        return value
```

The syntax may look hostile at the first glance, but don't worry about it now. When the time comes, you will learn how
field validators work, when exactly are they called, which validators to use (there are plenty!) and you will create
some of your own.

## Conclusion

This is the core idea behing Pydantic. It makes data validation simple for you. On top of that, you get
serialization / deserialization, type coercion, JSON schema generation, powerful model configuration and many other
tools that you will learn and master throughout the course. 