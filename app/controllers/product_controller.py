from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc

from app.models.product import Product
from app.requests.product_requests import StoreProductRequest, UpdateProductRequest, ListProductsRequest
from app.core.exceptions import NotFoundException, ConflictException


class ProductController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def index(self, request: ListProductsRequest) -> tuple[list[Product], int]:
        sort_map = {
            "id": Product.id,
            "name": Product.name,
            "price": Product.price,
            "created_at": Product.created_at,
        }
        col = sort_map[request.sort_by]
        order_fn = desc if request.order == "desc" else asc

        all_rows = await self.db.execute(select(Product))
        total = len(all_rows.scalars().all())

        result = await self.db.execute(
            select(Product).order_by(order_fn(col)).offset(request.skip).limit(request.limit)
        )
        return result.scalars().all(), total

    async def show(self, product_id: int) -> Product:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if not product:
            raise NotFoundException("Product not found")
        return product

    async def store(self, request: StoreProductRequest) -> Product:
        existing = await self.db.execute(select(Product).where(Product.slug == request.slug))
        if existing.scalars().first():
            raise ConflictException("A product with this slug already exists")

        product = Product(**request.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product_id: int, request: UpdateProductRequest) -> Product:
        product = await self.show(product_id)

        if request.slug and request.slug != product.slug:
            existing = await self.db.execute(select(Product).where(Product.slug == request.slug))
            if existing.scalars().first():
                raise ConflictException("A product with this slug already exists")

        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def destroy(self, product_id: int) -> None:
        product = await self.show(product_id)
        await self.db.delete(product)
        await self.db.commit()
