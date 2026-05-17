# Endterm SRE Microservices Project

End-to-end Site Reliability Engineering implementation for a distributed microservices system.

Student: Miras Aliyev  
Group: SE-2427

## Project Overview

This project demonstrates SRE practices for a containerized microservices application. It includes service decomposition, Docker-based deployment, Docker Swarm orchestration, Kubernetes manifests, Terraform infrastructure provisioning, Ansible automation, monitoring, alerting, incident simulation, recovery, and capacity planning.

The system contains six backend microservices, a frontend, an API gateway, PostgreSQL, Prometheus, and Grafana.

## Architecture

```text
User
  |
Frontend (Nginx, port 80)
  |
API Gateway (Nginx, port 8080)
  |
  +-- Auth Service    (8001)
  +-- User Service    (8002)
  +-- Product Service (8003)
  +-- Order Service   (8004)
  +-- Chat Service    (8005)
  +-- Payment Service (8006)
  |
PostgreSQL (5432)

Observability:
Prometheus (9090) -> Grafana (3000)
```

## Repository Structure

```text
services/       FastAPI microservices
frontend/       Nginx-served web UI
gateway/        Nginx API gateway configuration
monitoring/     Prometheus, alert rules, Grafana provisioning
incident/       Incident simulation override
k8s/            Kubernetes manifests
ansible/        Ansible inventory and playbooks
terraform/      Infrastructure as Code files
scripts/        Validation, load test, Swarm helper scripts
docs/           Report, postmortem, Terraform guide
evidence/       Screenshot evidence
```

## Prerequisites

- Docker Desktop
- Docker Compose
- Kubernetes enabled in Docker Desktop, or another local Kubernetes cluster
- WSL Ubuntu for Ansible
- Terraform
- PowerShell

Copy the example environment file if needed:

```powershell
Copy-Item .env.example .env
```

## Local Docker Compose Deployment

The main `docker-compose.yml` is also used for Swarm and therefore uses an overlay network. For local Docker Compose, use the Ansible/local override file:

```powershell
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml up --build -d
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml ps
```

Open:

- Frontend: http://localhost
- API Gateway: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana credentials:

```text
admin / admin123
```

Useful health checks:

```powershell
Invoke-RestMethod http://localhost:8080/auth/health
Invoke-RestMethod http://localhost:8080/users/health
Invoke-RestMethod http://localhost:8080/products/health
Invoke-RestMethod http://localhost:8080/orders/health
Invoke-RestMethod http://localhost:8080/chat/health
Invoke-RestMethod http://localhost:8080/payment/health
```

Stop local Compose:

```powershell
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml down
```

## Docker Swarm Deployment

Build local service images:

```powershell
.\scripts\build_swarm_images.ps1
```

Initialize Swarm if needed:

```powershell
docker swarm init
```

Deploy the stack:

```powershell
docker stack deploy -c docker-compose.yml app
```

Validate:

```powershell
docker stack ls
docker stack services app
docker stack ps app
docker network inspect app_application-network
```

The Swarm deployment uses the overlay network defined in `docker-compose.yml`.

## Kubernetes Deployment

Apply the Kubernetes manifest:

```powershell
kubectl apply -f k8s/microservices.yaml
```

Validate:

```powershell
kubectl get pods -n microservices
kubectl get deployments -n microservices
kubectl get svc -n microservices
kubectl get configmap -n microservices
kubectl get hpa -n microservices
```

Expected result:

```text
auth-service      1/1 Running
user-service      1/1 Running
product-service   1/1 Running
order-service     1/1 Running
chat-service      1/1 Running
payment-service   1/1 Running
postgres          1/1 Running
```

The Kubernetes manifest includes:

- `Namespace`
- `ConfigMap`
- `Deployment`
- `Service`
- `readinessProbe`
- `livenessProbe`
- `HorizontalPodAutoscaler`
- `imagePullPolicy: IfNotPresent` for local Docker Desktop images

## Ansible Automation

Run Ansible from WSL Ubuntu:

```bash
cd <project-directory>
ansible --version
ansible-playbook ansible/playbooks/install_docker.yml
ansible-playbook ansible/playbooks/deploy_compose.yml
```

The deployment playbook runs:

```bash
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml up --build -d
```

Successful evidence should show:

```text
PLAY RECAP
localhost : ok=3 changed=1 failed=0
```

## Terraform

Terraform files are located in `terraform/`.

```powershell
cd terraform
terraform init
terraform fmt -check -recursive
terraform plan
terraform apply
```

The Terraform configuration provisions cloud infrastructure such as networking, security rules, and a VM target for deployment. Configure real cloud credentials before running `terraform apply`.

Detailed notes are in:

```text
docs/terraform-guide.md
```

## Monitoring And Alerting

Prometheus configuration:

```text
monitoring/prometheus.yml
```

Alert rules:

```text
monitoring/alert_rules.yml
```

Grafana provisioning:

```text
monitoring/grafana/provisioning/
```

Useful pages:

- Prometheus targets: http://localhost:9090/targets
- Prometheus alerts: http://localhost:9090/alerts
- Grafana dashboards: http://localhost:3000

Implemented SRE signals:

- Availability
- Request rate
- Error rate
- Latency
- Service uptime
- Container health

## Incident Simulation

The incident simulates an Order Service failure caused by an incorrect database configuration.

Start the faulty configuration:

```powershell
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml -f incident/docker-compose.incident.yml up -d order-service
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml logs order-service
```

Expected impact:

- Order creation fails
- Order Service logs show database connection errors
- Monitoring detects degraded service behavior

Restore:

```powershell
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml up -d order-service
Invoke-RestMethod http://localhost:8080/orders/health
```

Postmortem:

```text
docs/incident-postmortem.md
```

## Capacity Planning

Load test helper:

```powershell
.\scripts\load_test_orders.ps1 -Requests 100 -DelayMilliseconds 50
```

Capacity findings:

- Order Service is the main request-path bottleneck.
- PostgreSQL can become a shared dependency bottleneck.
- Order and Payment workflows are the most sensitive user-facing paths.
- Horizontal scaling should prioritize Order Service replicas.
- Kubernetes HPA is defined for Order Service and Payment Service with `minReplicas: 1` and `maxReplicas: 3`.
- Database connection pooling should be added before heavy API scaling.

## Validation

Run configuration validation before deployment:

```powershell
.\scripts\validate_config.ps1
```

This checks environment variables, Docker Compose/Swarm configuration, gateway routes, Prometheus scrape targets, and health check endpoints.

## Evidence For Report

Recommended screenshots:

- `docker compose ... ps`
- `docker stack services app`
- `docker stack ps app`
- `kubectl get pods -n microservices`
- `kubectl get deployments -n microservices`
- `kubectl get svc -n microservices`
- `ansible --version`
- `ansible-playbook ansible/playbooks/deploy_compose.yml`
- Prometheus targets page
- Grafana dashboard
- Incident logs and recovery command output

## Final Deliverables

- Microservices source code
- Docker Compose and Docker Swarm configuration
- Kubernetes manifest
- Terraform IaC files
- Ansible automation playbooks
- Monitoring and alerting configuration
- Incident response and postmortem documentation
- Screenshot evidence
- Final PDF report with GitHub repository link
