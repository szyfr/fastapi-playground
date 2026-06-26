from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import require_admin
from app.controllers.product_controller import ProductController
from app.requests.product_requests import StoreProductRequest, UpdateProductRequest, ListProductsRequest
from app.responses import ProductResponse, PaginatedResponse, MessageResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def index(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", pattern="^(id|name|price|created_at)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    request = ListProductsRequest(skip=skip, limit=limit, sort_by=sort_by, order=order)
    controller = ProductController(db)
    products, total = await controller.index(request)
    return PaginatedResponse(
        data=[ProductResponse.model_validate(p) for p in products],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def show(product_id: int, db: AsyncSession = Depends(get_db)):
    controller = ProductController(db)
    product = await controller.show(product_id)
    return ProductResponse.model_validate(product)


@router.post("/", response_model=ProductResponse, status_code=201)
async def store(
    data: StoreProductRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    controller = ProductController(db)
    product = await controller.store(data)
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update(
    product_id: int,
    data: UpdateProductRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    controller = ProductController(db)
    product = await controller.update(product_id, data)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
async def destroy(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    controller = ProductController(db)
    await controller.destroy(product_id)
    return MessageResponse(message="Product deleted successfully")
