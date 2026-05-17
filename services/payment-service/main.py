from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from shared.metrics import MetricsMiddleware, metrics_response

service_name = "payment-service"
app = FastAPI(title="Payment Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


@app.get("/health")
async def health():
    return JSONResponse({"service": service_name, "status": "healthy"})


@app.get("/pay")
async def pay(amount: float = 0.0):
    # Simulated payment processing (stub)
    return {"status": "processed", "amount": amount}


@app.post("/pay")
async def pay_post(req: Request):
    data = await req.json()
    amount = data.get("amount", 0.0)
    # Simulated payment processing logic: always succeed for stub
    return {"status": "processed", "amount": amount}


@app.get("/metrics")
async def metrics():
    return metrics_response()
