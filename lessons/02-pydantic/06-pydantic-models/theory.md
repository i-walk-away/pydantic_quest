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
`UserFormDTO` with a wrong age type. Our type *hints* now become type *requirements* with no extra syntax.

### Validators

We can also create simple methods for validating the actual **values** of our model fields to enforce _business rules_.

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
