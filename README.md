# Containerized Microservices Incident Response Project

Student: Miras Aliyev  
Group: SE-2427  

This project implements a containerized microservices system with Terraform infrastructure files, monitoring, and an incident response simulation.

## Services

- Frontend served by Nginx on port `80`
- Nginx API gateway on port `8080`
- Authentication service on port `8001`
- User service on port `8002`
- Product service on port `8003`
- Order service on port `8004`
- Chat service on port `8005`
- PostgreSQL database on port `5432`
- Prometheus on port `9090`
- Grafana on port `3000`

## Prerequisites

- Windows 10 or Windows 11
- Docker Desktop
- Terraform
- A terminal such as PowerShell

## Run The System

```powershell
docker compose up --build -d
```

Open:

- Frontend: http://localhost
- Login page: http://localhost/login.html
- Register page: http://localhost/register.html
- Products page: http://localhost/products.html
- Orders page: http://localhost/orders.html
- Chat page: http://localhost/chat.html
- Status page: http://localhost/status.html
- API gateway: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana login:

- Username: `admin`
- Password: `admin123`

## Validate Services

```powershell
docker compose ps
docker compose logs order-service
```

Health checks:

```powershell
Invoke-RestMethod http://localhost:8080/auth/health
Invoke-RestMethod http://localhost:8080/users/health
Invoke-RestMethod http://localhost:8080/products/health
Invoke-RestMethod http://localhost:8080/orders/health
Invoke-RestMethod http://localhost:8080/chat/health
```

## Simulate The Incident

The incident introduces an incorrect PostgreSQL hostname for the Order Service.

```powershell
docker compose -f docker-compose.yml -f incident/docker-compose.incident.yml up -d order-service
docker compose logs order-service
```

Expected result:

- Order creation fails
- Order Service logs show a database connection error
- Prometheus target for the Order Service becomes unhealthy or returns failed metrics collection

## Restore The Service

```powershell
docker compose up -d order-service
```

Then test:

```powershell
Invoke-RestMethod http://localhost:8080/orders/health
```

## Terraform

Terraform files are in the `terraform` folder.
Detailed Terraform documentation is available in `docs/terraform-guide.md`.

```powershell
cd terraform
terraform init
terraform plan
terraform apply
```

Set real cloud credentials before applying. The configuration is written for AWS EC2.

## PDF Report

Open `docs/final-report.html` in a browser and print it as PDF. The report contains the required deployment guide, Terraform explanation, incident response report, postmortem, and screenshot evidence placeholders.
