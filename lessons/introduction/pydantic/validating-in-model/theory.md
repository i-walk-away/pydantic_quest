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

Now our function no longer has to care about the validity of the input data, becuase our Data Transfer Object
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

Invalid types raise `TypeError` and invalid values raise `ValueError` and all of this happens before data reaches actual
functions in the business logic layer.

Oh, and we just invented **Pydantic**!