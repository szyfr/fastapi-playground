from fastapi import APIRouter
from app.routes import product_routes, order_routes, auth_routes

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(product_routes.router)
router.include_router(order_routes.router)
