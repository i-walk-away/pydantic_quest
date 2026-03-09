from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


user = User(name="Alice", age=18)
