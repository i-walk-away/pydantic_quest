from pydantic import BaseModel


class HelloThere(BaseModel):
    salutations: str
    scope: str


hi = HelloThere(
    salutations='greetings',
    scope='everyone',
)
