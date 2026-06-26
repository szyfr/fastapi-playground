from pydantic import EmailStr, Field, field_validator
from app.requests.base_request import BaseRequest


def _validate_password_strength(v: str) -> str:
    if not any(c.isupper() for c in v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in v):
        raise ValueError("Password must contain at least one digit")
    return v


class RegisterRequest(BaseRequest):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    password_confirmation: str
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password_strength(v)

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseRequest):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UpdatePasswordRequest(BaseRequest):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirmation: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        return _validate_password_strength(v)

    @field_validator("new_password_confirmation")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v
