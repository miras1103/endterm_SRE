from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from shared.auth import get_current_user_id
from shared.database import run_database_command
from shared.metrics import MetricsMiddleware, metrics_response


service_name = "order-service"
app = FastAPI(title="Order Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


class OrderCreateRequest(BaseModel):
    product_id: int
    quantity: int


@app.on_event("startup")
def prepare_database():
    run_database_command(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )


@app.get("/health")
def get_health_status():
    run_database_command("SELECT 1")
    return {"service": service_name, "status": "healthy"}


@app.get("/orders")
def list_orders(current_user_id: int = Depends(get_current_user_id)):
    orders = run_database_command(
        """
        SELECT id, user_id, product_id, quantity, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (current_user_id,),
        fetch_all=True,
    )
    return {"orders": orders}


@app.post("/orders")
def create_order(order_request: OrderCreateRequest, current_user_id: int = Depends(get_current_user_id)):
    if order_request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    product = run_database_command(
        "SELECT id, available_quantity FROM products WHERE id = %s",
        (order_request.product_id,),
        fetch_one=True,
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["available_quantity"] < order_request.quantity:
        raise HTTPException(status_code=409, detail="Not enough product stock")

    order = run_database_command(
        """
        INSERT INTO orders (user_id, product_id, quantity, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, product_id, quantity, status, created_at
        """,
        (current_user_id, order_request.product_id, order_request.quantity, "created"),
        fetch_one=True,
    )
    run_database_command(
        "UPDATE products SET available_quantity = available_quantity - %s WHERE id = %s",
        (order_request.quantity, order_request.product_id),
    )
    return order


@app.get("/metrics")
def get_metrics():
    return metrics_response()
