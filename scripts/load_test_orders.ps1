param(
    [int]$Requests = 60,
    [int]$DelayMilliseconds = 100
)

$ErrorActionPreference = "Stop"
$ordersHealthUrl = "http://localhost:8080/orders/health"
$success = 0
$failed = 0
$durations = New-Object System.Collections.Generic.List[double]

Write-Host "Running lightweight Order Service capacity test: $Requests requests"

for ($i = 1; $i -le $Requests; $i++) {
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-RestMethod -Uri $ordersHealthUrl -TimeoutSec 5 | Out-Null
        $success++
    }
    catch {
        $failed++
    }
    finally {
        $timer.Stop()
        $durations.Add($timer.Elapsed.TotalMilliseconds)
    }

    Start-Sleep -Milliseconds $DelayMilliseconds
}

$average = ($durations | Measure-Object -Average).Average
$maximum = ($durations | Measure-Object -Maximum).Maximum
$rps = if (($Requests * $DelayMilliseconds) -gt 0) { 1000 / $DelayMilliseconds } else { 0 }

Write-Host "Successful requests: $success"
Write-Host "Failed requests: $failed"
Write-Host ("Average latency: {0:N2} ms" -f $average)
Write-Host ("Maximum latency: {0:N2} ms" -f $maximum)
Write-Host ("Approximate generated request rate: {0:N2} RPS" -f $rps)
Write-Host "Check Grafana and Prometheus after the test for CPU, latency, request rate, and error-rate changes."
