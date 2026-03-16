from pydantic import BaseModel


class Pirate(BaseModel):
    name: str
    gold: float
    crimes: list[str]
