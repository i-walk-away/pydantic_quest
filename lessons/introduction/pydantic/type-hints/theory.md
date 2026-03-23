### But what about type hints?

Since Python 3.5, we can add *hints* about our variables' types:

```python
x: int = 78                                # x should be an integer
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

But they're called type *hints* for a reason. You can STILL go Rambo and run the code above, and it will still fail
only when `"18 + 1 is attempted

Or you can do this:

```python
x: int = 78
x = "Rambo"
```

This is a valid python program that will not refuse to run. Correct typing is NOT **enforced at runtime**.
