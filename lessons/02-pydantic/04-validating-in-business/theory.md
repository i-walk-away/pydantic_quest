### Validating data in the business logic layer

There are some ways to work around this issue. Let's start by simply modifying our function to check if the passed
values are of correct types:

```python
def calculate_age(data: UserFormDTO) -> str:
    if not isinstance(data.age, int):                      # check if data.age is not an instance of class 'int'
        raise TypeError(f'{data.age} is not an integer!')  # if so, exit early with an error 

    response = f"{data.username} will be {data.age + 1} years old next year!"
    return response
```

Although broken data still makes it into the function that uses it, this small check prevents our function from wasting
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

Example below is *a little bit* exaggerated, but it does show the problem with scaling. 

// note to self: raise exceptions instead of returning none

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
3. Data validation itself is *beyond the scope* of the code that should be doing the actual work. Its main job should not
   be to check whether the input was valid in the first place

Looks like validating data inside the function doesn't cut it. There is a better way though - and it's to implement data
validation in our *model istelf* - in the `UserFormDTO` class.
