from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time


request_counter = Counter(
    "service_http_requests_total",
    "Total HTTP requests processed by the service",
    ["service_name", "method", "path", "status_code"],
)

request_duration = Histogram(
    "service_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["service_name", "method", "path"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        request_path = request.url.path
        request_counter.labels(
            self.service_name,
            request.method,
            request_path,
            response.status_code,
        ).inc()
        request_duration.labels(
            self.service_name,
            request.method,
            request_path,
        ).observe(duration)
        return response


def metrics_response():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
