from typing import Optional
from pydantic import Field, field_validator
from app.requests.base_request import BaseRequest


class StoreProductRequest(BaseRequest):
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def name_not_only_digits(cls, v):
        if v.strip().isdigit():
            raise ValueError("Product name cannot be only numbers")
        return v.strip()

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v):
        v = v.lower().strip()
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("Slug may only contain lowercase letters, numbers, and hyphens")
        return v


class UpdateProductRequest(BaseRequest):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ListProductsRequest(BaseRequest):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: str = Field(default="id", pattern="^(id|name|price|created_at)$")
    order: str = Field(default="asc", pattern="^(asc|desc)$")
