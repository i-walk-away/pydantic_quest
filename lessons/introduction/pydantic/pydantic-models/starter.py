from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    age: int
    email: EmailStr
