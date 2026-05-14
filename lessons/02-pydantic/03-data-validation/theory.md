
## Data validation

Imagine you have a website that calculates how old you will be when you're 1 year older. This may not be the most
useful website, but it gives us something to work with.

The user is prompted to fill in this data:

```text
Enter your username: ...
Enter your age: ...
```

For the sake of simplicity, assume that after the form is filled and sent, it immediately
enters our codebase as this object:

```python
filled_form = {
    "username": "Arbitrary username", 
    "age": 10000
}
```

Where the actual values are inputed by the user who fills the form.

Then imagine that user's input for this specific form is mapped to a small object like this:

```python
@dataclass
class UserFormDTO:
    username: str
    age: int
    # for each existing field of our filled form, there is a corresponding field in the DTO 
```

A DTO, or *Data Transfer Object*, is just a small object whose sole job is to carry structured data
from one part of the program to another. Data submitted by the user gets gathered into a single `UserFormDTO` object, 
with its `username` and `age` values copied from the raw request. 

This is just an input data container. We basically build a `UserFormDTO` out of the request data.  

So when the user sends:

```python
filled_form = {"username": "Adolf", "age": 20}
```

we build a UserFormDTO object out of it, with `username="Adolf"` and `age=20`. A little illustration in case you
struggle with understanding the whole picture at this point:

```python
@dataclass
class UserFormDTO:
    username: str
    age: int


# user submitted data
filled_form = {
    "username": "Adolf", 
    "age": 20
} 

# here it is mapped to a DTO object for further usage
dto_object = UserFormDTO(
    username=filled_form.get("username"),
    age=filled_form.get("age")
)
```

and then pass it to the funcion that uses it to calculate age, which looks like this:

```python
def calculate_age(data: UserFormDTO) -> str:
    calculated_age = data.age + 1
    response = f"{data.username} will be {calculated_age} years old next year!"
    
    return response
```

Let's recap the path that our data takes:

1. User sends `username` and `age`
2. we build a `UserFormDTO` out of this data
3. we call `calculate_age` and pass the DTO as an argument to it
4. The age is calculated
5. the result is returned to the user

## The issue

There is a problem though. This system assumes two things are true:

- `username` is actually a string
- `age` is actually an integer

But what if the incoming data looks like this?

```python
filled_form = {
    "username": "Alice", 
    "age": "Albania"  # invalid
}
```

The user was a little bit silly and sent us 'Albania' as their age. This is clearly not an integer. The data was
broken from the very beginning. When _exactly_ will our program fail?


1. ✓ User sends `username: "Alice"` and `age: "Albania"` to our API
2. ✓ We build a UserFormDTO out of this data
3. ✓ We call `calculate_age` and pass the DTO as an argument to it 
4. X The age is calculated -- -- *runtime error upon trying to add 1 to a string*
5. ...


The broken data made quite a long jorney through our program before something exploded. It shouldn't have even
**reached** the actual function that uses it, and instead should've been rejected immediately on step 2, becuase the data
was broken:


1. ✓ User sends `username: "Alice"` and `age: "Albania"` to our API 
2. X We build a `UserFormDTO` out of this data -- -- *Validation error: couldn't assign `"Albania"` to `UserFormDTO.age`,
   because `UserFormDTO` expects age to be an integer and the user had sent a string instead*


Statically typed language like Java would fail with a runtime error on step 2. Python, however, allowed that.

## Assignment

Complete the quiz.