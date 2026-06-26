from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.requests.order_requests import StoreOrderRequest, CancelOrderRequest, ListOrdersRequest
from app.core.exceptions import NotFoundException, BadRequestException, UnprocessableEntityException


class OrderController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def index(self, user_id: int, request: ListOrdersRequest) -> tuple[list[Order], int]:
        query = select(Order).where(Order.user_id == user_id)

        if request.status:
            query = query.where(Order.status == request.status)

        all_rows = await self.db.execute(query)
        total = len(all_rows.scalars().all())

        result = await self.db.execute(
            query.order_by(desc(Order.created_at)).offset(request.skip).limit(request.limit)
        )
        return result.scalars().all(), total

    async def show(self, order_id: int, user_id: int) -> Order:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalars().first()
        if not order:
            raise NotFoundException("Order not found")
        return order

    async def create_order(self, user_id: int, request: StoreOrderRequest) -> Order:
        # Validate inventory
        for item in request.items:
            product = await self._get_product(item.product_id)
            if product.stock < item.quantity:
                raise UnprocessableEntityException(
                    f"Insufficient stock for '{product.name}'",
                    details={"product_id": item.product_id, "available": product.stock},
                )

        order = Order(
            user_id=user_id,
            total=sum(item.price * item.quantity for item in request.items),
            shipping_address=request.shipping_address,
            coupon_code=request.coupon_code,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()  # Get order.id before committing

        for item in request.items:
            self.db.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            ))

        await self.db.commit()
        await self.db.refresh(order)

        # TODO: await fire_capi_event("Purchase", order)
        # TODO: await clear_cart(user_id)

        return order

    async def cancel_order(self, order_id: int, user_id: int, request: CancelOrderRequest) -> Order:
        order = await self.show(order_id, user_id)

        if order.status != OrderStatus.PENDING:
            raise BadRequestException(
                f"Only pending orders can be cancelled. Current status: {order.status}"
            )

        order.status = OrderStatus.CANCELLED
        order.cancel_reason = request.reason
        order.refund_method = request.refund_method

        await self.db.commit()
        await self.db.refresh(order)

        # TODO: await stripe_refund(order)
        # TODO: await fire_capi_event("CancelOrder", order)

        return order

    async def _get_product(self, product_id: int) -> Product:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if not product:
            raise NotFoundException(f"Product {product_id} not found")
        return product
