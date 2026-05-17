# Incident Postmortem: Order Service Database Misconfiguration

## Summary

The simulated incident caused the Order Service to lose access to PostgreSQL because of an incorrect database hostname. The rest of the system stayed available, but order creation was degraded until the configuration was restored.

## Impact

- Order creation was unavailable during the incident.
- Product, authentication, user, chat, payment, frontend, Prometheus, and Grafana continued running.
- Monitoring and logs exposed the failure through service health and database connection errors.

## Root Cause

The incident override changed the Order Service database connection to an invalid PostgreSQL host. As a result, the service could not establish a database connection during order-related requests.

## Detection

- Order workflow failed from the frontend/API gateway.
- Order Service logs showed database connectivity errors.
- Prometheus targets and Grafana dashboards showed degraded service behavior.

## Recovery

The faulty incident override was removed and the Order Service was redeployed with the correct `DATABASE_URL`.

```powershell
docker compose -f docker-compose.yml -f ansible/docker-compose.local.yml up -d order-service
Invoke-RestMethod http://localhost:8080/orders/health
```

## Preventive Actions

- Keep deployment validation in `scripts/validate_config.ps1`.
- Use health checks and restart policies for backend services.
- Monitor service availability, error rate, and latency in Prometheus and Grafana.
- Store known-good environment values in `.env.example`.
