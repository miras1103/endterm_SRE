FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/shared ./shared
COPY services/auth-service ./service
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
