from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.requests.base_request import BaseRequest


class OrderItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    price: float = Field(..., gt=0)


class StoreOrderRequest(BaseRequest):
    items: List[OrderItemRequest] = Field(..., min_length=1, max_length=50)
    shipping_address: Optional[str] = Field(None, max_length=500)
    coupon_code: Optional[str] = Field(None, max_length=50, pattern="^[A-Z0-9-]*$")

    @field_validator("items")
    @classmethod
    def no_duplicate_products(cls, v):
        ids = [item.product_id for item in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Order cannot contain duplicate product IDs")
        return v


class CancelOrderRequest(BaseRequest):
    reason: Optional[str] = Field(None, max_length=500)
    refund_method: str = Field(default="original", pattern="^(original|store_credit)$")


class ListOrdersRequest(BaseRequest):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    status: Optional[str] = Field(
        None,
        pattern="^(pending|processing|completed|cancelled|refunded)$",
    )
