from pydantic import BaseModel, field_validator


class BaseRequest(BaseModel):
    """Base request — shared config and sanitization."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("*", mode="before")
    @classmethod
    def strip_empty_strings(cls, v):
        if v == "":
            return None
        return v
