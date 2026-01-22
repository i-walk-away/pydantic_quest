from pydantic import BaseModel, ConfigDict


class ExtendedBaseModel(BaseModel):
    """
    Base DTO with shared model configuration.
    """
    model_config = ConfigDict(extra="ignore")
