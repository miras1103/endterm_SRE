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

## Assignment 6 We Added

Assignment 6 extends the previous incident response and Terraform work with SRE automation, monitoring-based alerting, and capacity planning for the Dockerized microservices system.

### Automation Mechanisms

- Added `restart: unless-stopped` policies for the application, database, gateway, frontend, Prometheus, and Grafana containers.
- Added Docker health checks for the backend microservices using their HTTP `/health` endpoints.
- Added health checks for the API gateway and frontend.
- Added an API gateway `/health` endpoint in `gateway/nginx.conf`.
- Connected Prometheus alert rules through `monitoring/alert_rules.yml`.
- Added pre-deployment validation in `scripts/validate_config.ps1` to check important configuration before deployment.

Run validation before starting the system:

```powershell
.\scripts\validate_config.ps1
docker compose up --build -d
```

The validation script checks:

- Required environment variables in `.env`.
- Matching variables in `.env.example` as the deployment template.
- Correct PostgreSQL `DATABASE_URL` format and Docker hostname.
- Template variable usage in `docker-compose.yml` and `docker-stack.yml`.
- API gateway upstream endpoints for all backend services.
- Prometheus scrape endpoints and Docker health check URLs.

### Monitoring And Alerting

Prometheus now loads alert rules from:

```text
monitoring/alert_rules.yml
```

Implemented alert conditions:

- `ServiceDown`: triggers when Prometheus cannot scrape a service.
- `HighErrorRate`: triggers when 5xx responses are above 5 percent.
- `HighLatency`: triggers when p95 request latency is above 1 second.

Useful Prometheus pages:

- Targets: http://localhost:9090/targets
- Alerts: http://localhost:9090/alerts

### Capacity Planning

The system capacity is analyzed using Prometheus metrics and a lightweight load script:

```powershell
.\scripts\load_test_orders.ps1 -Requests 100 -DelayMilliseconds 50
```

Metrics used for capacity analysis:

- CPU usage and memory utilization from containers
- Request rate through `service_http_requests_total`
- Error rate through HTTP `5xx` responses
- Response latency through `service_http_request_duration_seconds`
- Container health and restart behavior through Docker

Observed capacity risks:

- Order Service becomes the main bottleneck under increased request load.
- Response time increases when the Order Service or database is saturated.
- Error rates may increase if database connections or CPU resources are insufficient.
- PostgreSQL can become a shared bottleneck because Product and Order workflows both depend on it.

### Scaling Strategy

Recommended scaling approach:

- Horizontally scale the Order Service when request rate increases.
- Add a load balancer or orchestration platform such as Kubernetes for multiple service replicas.
- Vertically scale the VM with Terraform by increasing `instance_type` in `terraform/terraform.tfvars`.
- Add database connection pooling before scaling API replicas heavily.
- Optimize database queries and indexes if latency grows during load tests.

Current Terraform capacity setting:

```hcl
instance_type = "t3.micro"
```

For higher load, change it for example to:

```hcl
instance_type = "t3.small"
```

Then apply:

```powershell
cd terraform
terraform plan
terraform apply
```

### Evidence To Include In The PDF

Recommended screenshots for Assignment 6:

- `docker compose ps` showing healthy services.
- Prometheus targets page showing all services as up.
- Prometheus alerts page showing configured rules.
- Grafana dashboard during normal load.
- Grafana dashboard or Prometheus metrics during load test.
- Order Service recovery after stopping or misconfiguring the container.

### Summary

For Assignment 6, we added automation for deployment safety, service recovery, health checking, monitoring alerts, configuration validation, and basic load testing. We also documented capacity risks and scaling strategies based on SRE principles.
