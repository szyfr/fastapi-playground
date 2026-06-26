from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.db import get_db
from app.core.deps import get_current_user
from app.controllers.order_controller import OrderController
from app.requests.order_requests import StoreOrderRequest, CancelOrderRequest, ListOrdersRequest
from app.responses import OrderResponse, PaginatedResponse
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def index(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|processing|completed|cancelled|refunded)$"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request = ListOrdersRequest(skip=skip, limit=limit, status=status)
    controller = OrderController(db)
    orders, total = await controller.index(user.id, request)
    return PaginatedResponse(
        data=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def show(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    controller = OrderController(db)
    order = await controller.show(order_id, user.id)
    return OrderResponse.model_validate(order)


@router.post("/", response_model=OrderResponse, status_code=201)
async def store(
    data: StoreOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    controller = OrderController(db)
    order = await controller.create_order(user.id, data)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel(
    order_id: int,
    data: CancelOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    controller = OrderController(db)
    order = await controller.cancel_order(order_id, user.id, data)
    return OrderResponse.model_validate(order)
