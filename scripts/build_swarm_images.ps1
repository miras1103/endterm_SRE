$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Resolve-Path (Join-Path $scriptDir '..')

$services = @(
    @{ Name = 'auth-service'; Path = 'services/auth-service' },
    @{ Name = 'user-service'; Path = 'services/user-service' },
    @{ Name = 'product-service'; Path = 'services/product-service' },
    @{ Name = 'order-service'; Path = 'services/order-service' },
    @{ Name = 'chat-service'; Path = 'services/chat-service' },
    @{ Name = 'payment-service'; Path = 'services/payment-service' }
)

foreach ($service in $services) {
    $serviceRoot = Join-Path $rootDir $service.Path
    Write-Host "Building image $($service.Name):latest from $serviceRoot"
    docker build -t "$($service.Name):latest" -f "$serviceRoot\Dockerfile" "$rootDir"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed for $($service.Name)"
        exit $LASTEXITCODE
    }
}

Write-Host 'All Swarm service images built successfully.'
