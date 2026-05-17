$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-Path (Join-Path $scriptDir '..')
Push-Location $scriptDir

Write-Host 'Checking Docker Swarm status...'
$swarmState = docker info --format '{{.Swarm.LocalNodeState}}' 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Unable to query Docker info. Is Docker running?'
    Pop-Location
    exit 1
}

if ($swarmState -ne 'active') {
    Write-Host 'Initializing Docker Swarm...'
    docker swarm init | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'Failed to initialize Docker Swarm.'
        Pop-Location
        exit $LASTEXITCODE
    }
} else {
    Write-Host 'Docker Swarm is already active.'
}

Write-Host 'Building Swarm service images...'
& "$scriptDir\build_swarm_images.ps1"
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    exit $LASTEXITCODE
}

Write-Host 'Deploying stack app...'
docker stack deploy -c "$rootDir\docker-compose.yml" app
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Stack deploy failed.'
    Pop-Location
    exit $LASTEXITCODE
}

Write-Host 'Stack app deployed successfully.'
Pop-Location
