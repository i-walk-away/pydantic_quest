from dataclasses import dataclass

from pydantic import BaseModel


class WildUserFormDTO(BaseModel):
    username: str
    age: int


@dataclass
class CleanUserFormDTO:
    username: str
    age: int
