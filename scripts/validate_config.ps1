param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$StackFile = "docker-stack.yml",
    [string]$EnvFile = ".env",
    [string]$EnvTemplateFile = ".env.example"
)

$ErrorActionPreference = "Stop"

function Read-EnvFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "Environment file was not found: $Path"
    }

    $values = @{}
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) {
            return
        }

        $parts = $line -split "=", 2
        if ($parts.Count -ne 2 -or $parts[0].Trim() -eq "") {
            throw "Invalid environment line in ${Path}: $line"
        }

        $values[$parts[0].Trim()] = $parts[1].Trim()
    }

    return $values
}

function Require-File {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "Required configuration file was not found: $Path"
    }
}

function Require-Text {
    param(
        [string]$Text,
        [string]$Expected,
        [string]$Description
    )

    if ($Text -notlike "*$Expected*") {
        throw "Configuration validation failed. Missing ${Description}: $Expected"
    }
}

function Require-Port {
    param(
        [hashtable]$Env,
        [string]$Name
    )

    $port = 0
    if (-not [int]::TryParse($Env[$Name], [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
        throw "Environment variable $Name must be a TCP port between 1 and 65535."
    }
}

$requiredEnvVars = @(
    "APP_ENV",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "DATABASE_URL",
    "JWT_SECRET",
    "GRAFANA_ADMIN_USER",
    "GRAFANA_ADMIN_PASSWORD",
    "FRONTEND_PORT",
    "API_GATEWAY_PORT",
    "POSTGRES_PORT",
    "PROMETHEUS_PORT",
    "GRAFANA_PORT"
)

Require-File $ComposeFile
Require-File $StackFile
Require-File $EnvTemplateFile

$envValues = Read-EnvFile $EnvFile
$templateValues = Read-EnvFile $EnvTemplateFile

foreach ($name in $requiredEnvVars) {
    if (-not $envValues.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($envValues[$name])) {
        throw "Missing required environment variable in ${EnvFile}: $name"
    }

    if (-not $templateValues.ContainsKey($name)) {
        throw "Missing required environment variable in ${EnvTemplateFile}: $name"
    }
}

Require-Port $envValues "FRONTEND_PORT"
Require-Port $envValues "API_GATEWAY_PORT"
Require-Port $envValues "POSTGRES_PORT"
Require-Port $envValues "PROMETHEUS_PORT"
Require-Port $envValues "GRAFANA_PORT"

$databaseUrlPattern = "^postgresql://([^:]+):([^@]+)@([^:/]+):([0-9]+)/(.+)$"
if ($envValues["DATABASE_URL"] -notmatch $databaseUrlPattern) {
    throw "DATABASE_URL must use this format: postgresql://user:password@host:port/database"
}

if ($Matches[1] -ne $envValues["POSTGRES_USER"]) {
    throw "DATABASE_URL user does not match POSTGRES_USER."
}

if ($Matches[2] -ne $envValues["POSTGRES_PASSWORD"]) {
    throw "DATABASE_URL password does not match POSTGRES_PASSWORD."
}

if ($Matches[3] -ne "postgres") {
    throw "DATABASE_URL host must be 'postgres' for Docker service networking."
}

if ($Matches[4] -ne "5432") {
    throw "DATABASE_URL internal database port must be 5432."
}

if ($Matches[5] -ne $envValues["POSTGRES_DB"]) {
    throw "DATABASE_URL database name does not match POSTGRES_DB."
}

if ($envValues["JWT_SECRET"] -eq "local-development-secret") {
    Write-Warning "JWT_SECRET uses the local development value. Replace it before production deployment."
}

$composeText = Get-Content $ComposeFile -Raw
$stackText = Get-Content $StackFile -Raw
$gatewayText = Get-Content "gateway/nginx.conf" -Raw
$prometheusText = Get-Content "monitoring/prometheus.yml" -Raw

$composeTemplateVars = @(
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "DATABASE_URL",
    "JWT_SECRET",
    "GRAFANA_ADMIN_USER",
    "GRAFANA_ADMIN_PASSWORD",
    "FRONTEND_PORT",
    "API_GATEWAY_PORT",
    "POSTGRES_PORT",
    "PROMETHEUS_PORT",
    "GRAFANA_PORT"
)

foreach ($name in $composeTemplateVars) {
    $composeVariableToken = '${' + $name
    Require-Text $composeText $composeVariableToken "compose template variable"
}

$stackTemplateVars = @(
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "DATABASE_URL",
    "JWT_SECRET",
    "GRAFANA_ADMIN_USER",
    "GRAFANA_ADMIN_PASSWORD",
    "FRONTEND_PORT",
    "API_GATEWAY_PORT",
    "PROMETHEUS_PORT",
    "GRAFANA_PORT"
)

foreach ($name in $stackTemplateVars) {
    $stackVariableToken = '${' + $name
    Require-Text $stackText $stackVariableToken "stack template variable"
}

$expectedEndpoints = @{
    "auth-service" = "8001"
    "user-service" = "8002"
    "product-service" = "8003"
    "order-service" = "8004"
    "chat-service" = "8005"
    "payment-service" = "8006"
}

foreach ($serviceName in $expectedEndpoints.Keys) {
    $port = $expectedEndpoints[$serviceName]
    Require-Text $gatewayText "server ${serviceName}:${port}" "gateway upstream endpoint"
    Require-Text $prometheusText "${serviceName}:${port}" "Prometheus scrape endpoint"
    Require-Text $composeText "http://localhost:${port}/health" "service health check endpoint"
}

Require-Text $gatewayText "location /health" "API gateway health endpoint"
Require-Text $composeText "./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml:ro" "Prometheus alert rules mount"

docker compose config | Out-Null

Write-Host "Configuration validation passed."
Write-Host "Checked required environment variables, .env template, DATABASE_URL, compose templates, gateway endpoints, Prometheus targets, and health checks."
