## Dynamics

Python is a dynamically typed language. It means that the *type* of the objects (variables, functions)
can change throughout the object's lifecycle:

```python
var = 12
var = "string"  # <-- statically typed languages would execute you on spot for this
```

To be precise, it's not that the type of a variable changes - it's that in python, variables themselves don't have a
type *at all*.

```python
var = 12        # var references an integer object. it POINTS to an int object
var = "string"  # var now references a string object
```

In statically typed languages like Java this woudln't work:

```java
int x = 12;   // x is declared as integer
x = "hello";  // compile error - x can only hold integers
```

Dynamic typing has _some_ benefits to it, but we will focus solely on the downsides (you generally should not do that in
life).

### Consequences

The main downside is that wrong data often survives longer than it should.

For example:

```python
def calculate_age_next_year(age):
    return age + 1


calculate_age_next_year("18")  # ValueError: we passed a string here, can't add +1 to a str
```

This code crashes only when `+ 1` is attempted, not when `age` of invalid *type* was passed to it.
The function did not reject the value and attempted to work with it, even though the value was wrong for the job.

That is not very convenient. Python lets values move through the program very freely, and the errors may happen far away
from where the bad data first entered the system.
