
## Data validation

Imagine you have a website that calculates how old you will be when you're 1 year older. This may not be the most
useful website, but it gives us something to work with.

The user is prompted to fill in this data:

```text
Enter your username: ...
Enter your age: ...
```

The user submits this data, your backend receives it, and then your code uses it.
A simplified path looks like this:

1. we receive `username` and `age` from the user
2. that data used somewhere (`age + 1` is calculated)
3. the result is returned to the user

Now imagine that user's input for this specific form is mapped to a small object like this:

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

we build a UserFormDTO object out of it, with `username`="Adolf" and `age`=20, and then pass it to the funcion that uses
it to calculate age.

Then the actual function may look like this:

```python
def calculate_age(data: UserFormDTO) -> str:
    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

We can now see a less simplified path of our data:

1. User sends `username` and `age`
2. we build a `UserFormDTO` out of this data
3. we call `calculate_age` and pass the DTO as an argument to it
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
2. We build a UserFormDTO out of this data -- -- -- -- -- -- -- -- - ✓
3. We call `calculate_age` and pass the DTO as an argument to it --- ✓
4. The age is calculated <-------- X *runtime error upon trying to add 1 to a string*
5. ...

The broken data made quite a long jorney through our program before something exploded. It shouldn't have even
**reached** the actual function that uses it and instead should've been rejected immediately on step 2, becuase the data
was broken:

1. User sends `username: "Alice"` and `age: "Albania"` to our API -- ✓
2. We build a `UserFormDTO` out of this data <----- *Validation error: couldn't assign `"Albania"` to `UserFormDTO.age`,
   because `UserFormDTO` expects age to be an integer and user sent string instead*

Statically typed language like Java would fail with a runtime error on step 2. But Python allows that.
