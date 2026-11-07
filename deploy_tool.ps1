# deploy_tool.ps1
# Imports the updated risk_scorer.py (v2 engine) into watsonx Orchestrate.
# Run from the repo root:  .\deploy_tool.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# 1. Load .env
# ---------------------------------------------------------------------------
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found."
    exit 1
}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and $line -notmatch "^#" -and $line -match "=") {
        $parts = $line -split "=", 2
        Set-Item -Path "Env:\$($parts[0].Trim())" -Value $parts[1].Trim().Trim('"').Trim("'")
    }
}

foreach ($var in @("WATSONX_APIKEY", "WATSONX_URL")) {
    if ([string]::IsNullOrWhiteSpace((Get-Item "Env:\$var" -ErrorAction SilentlyContinue).Value)) {
        Write-Error "Missing required variable: $var"
        exit 1
    }
}
Write-Host "Loaded .env" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 2. Activate environment
# ---------------------------------------------------------------------------
Write-Host "Activating environment ..." -ForegroundColor Cyan
"Y" | orchestrate env add --name "online-safety-companion" --url $env:WATSONX_URL --type ibm_iam 2>&1 | Out-Null
orchestrate env activate "online-safety-companion" --api-key $env:WATSONX_APIKEY
if ($LASTEXITCODE -ne 0) { Write-Error "Authentication failed."; exit 1 }
Write-Host "Authenticated." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Import the updated risk_scorer tool (score_risk function, v2 engine)
# ---------------------------------------------------------------------------
Write-Host "Importing risk_scorer.py as 'score_risk' tool ..." -ForegroundColor Cyan
orchestrate tools import --file "tools/risk_scorer.py" --kind python
if ($LASTEXITCODE -ne 0) { Write-Error "Tool import failed."; exit 1 }
Write-Host "Tool imported successfully." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 4. Verify
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Deployed tools:" -ForegroundColor Cyan
orchestrate tools list

Write-Host ""
Write-Host "Done. The score_risk tool now uses the v2 engine." -ForegroundColor Green
