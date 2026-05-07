$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
$SeedDir = Join-Path $ProjectRoot "db/seeds"

$ContainerName = if ($env:CONTAINER_NAME) { $env:CONTAINER_NAME } else { "d2c-postgres" }
$DbName = if ($env:DB_NAME) { $env:DB_NAME } else { "d2c_commerce" }
$DbUser = if ($env:DB_USER) { $env:DB_USER } else { "postgres" }

$SeedFiles = @(
    "seed_categories.sql",
    "seed_campaigns.sql",
    "seed_products.sql",
    "seed_coupons.sql"
)

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "docker command not found."
    exit 1
}

$RunningContainer = docker ps --format '{{.Names}}' | Where-Object { $_ -eq $ContainerName }
if (-not $RunningContainer) {
    Write-Error "Container '$ContainerName' is not running."
    exit 1
}

foreach ($file in $SeedFiles) {
    $fullPath = Join-Path $SeedDir $file

    if (-not (Test-Path $fullPath -PathType Leaf)) {
        Write-Error "Seed file not found: $fullPath"
        exit 1
    }

    Write-Host "Applying $file ..." -ForegroundColor Cyan

    Get-Content -Raw $fullPath | docker exec -i $ContainerName psql `
        -v ON_ERROR_STOP=1 `
        -U $DbUser `
        -d $DbName

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to apply $file"
        exit 1
    }
}

Write-Host "All seed files applied successfully." -ForegroundColor Green