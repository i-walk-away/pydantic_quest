from pydantic import BaseModel


class UserProfile(BaseModel):
    """
    contributor note:
    this starter intentionally gives structure but not implementation.

    1) add these fields:
       - username: str
       - age: int
       - tags: list[str] = []
    2) add validation:
       - username must not be blank (strip spaces first)
       - age must be between 13 and 120
    3) keep class name and field names unchanged (cases depend on them)
    """

    pass
