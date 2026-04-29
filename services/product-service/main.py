from fastapi import FastAPI
from pydantic import BaseModel

from shared.database import run_database_command
from shared.metrics import MetricsMiddleware, metrics_response


service_name = "product-service"
app = FastAPI(title="Product Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


class ProductCreateRequest(BaseModel):
    name: str
    description: str
    price: float
    available_quantity: int


@app.on_event("startup")
def prepare_database():
    run_database_command(
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            available_quantity INTEGER NOT NULL
        )
        """
    )
    run_database_command(
        """
        INSERT INTO products (name, description, price, available_quantity)
        VALUES
            ('Laptop', 'Portable workstation for study and development', 899.00, 15),
            ('Headphones', 'Wireless headphones with clear microphone', 79.00, 40),
            ('Keyboard', 'Mechanical keyboard for daily work', 49.00, 30)
        ON CONFLICT DO NOTHING
        """
    )


@app.get("/health")
def get_health_status():
    return {"service": service_name, "status": "healthy"}


@app.get("/products")
def list_products():
    products = run_database_command(
        "SELECT id, name, description, price, available_quantity FROM products ORDER BY id",
        fetch_all=True,
    )
    return {"products": products}


@app.post("/products")
def create_product(product_request: ProductCreateRequest):
    product = run_database_command(
        """
        INSERT INTO products (name, description, price, available_quantity)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, description, price, available_quantity
        """,
        (
            product_request.name,
            product_request.description,
            product_request.price,
            product_request.available_quantity,
        ),
        fetch_one=True,
    )
    return product


@app.get("/metrics")
def get_metrics():
    return metrics_response()
