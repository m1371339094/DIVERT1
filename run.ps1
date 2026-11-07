# run.ps1
# Deploy Online Safety Companion to IBM watsonx Orchestrate.
# Run from the repo root:  .\run.ps1
# Requires: ibm-watsonx-orchestrate installed  (pip install ibm-watsonx-orchestrate)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# 1. Load .env into the current PowerShell session
# ---------------------------------------------------------------------------
$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found at $envFile"
    exit 1
}

Write-Host "`n==> Loading .env ..." -ForegroundColor Cyan

Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and $line -notmatch "^#") {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $key   = $parts[0].Trim()
            $value = $parts[1].Trim().Trim('"').Trim("'")
            Set-Item -Path "Env:\$key" -Value $value
            Write-Host "    Loaded: $key" -ForegroundColor DarkGray
        }
    }
}

# ---------------------------------------------------------------------------
# 2. Validate required variables
# ---------------------------------------------------------------------------
foreach ($var in @("WATSONX_APIKEY", "WATSONX_URL")) {
    if ([string]::IsNullOrWhiteSpace((Get-Item "Env:\$var" -ErrorAction SilentlyContinue).Value)) {
        Write-Error "Required variable '$var' is missing or empty in .env"
        exit 1
    }
}
Write-Host "    All required variables found." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Register + activate the environment
#    'orchestrate env add' registers the URL, then 'env activate' authenticates.
#    If the env already exists, 'add' will fail — so we suppress that error
#    and go straight to activate.
# ---------------------------------------------------------------------------
$envName = "online-safety-companion"

Write-Host "`n==> Registering environment '$envName' ..." -ForegroundColor Cyan
# Pipe "Y" to silently confirm the update prompt if env already exists
"Y" | orchestrate env add --name $envName --url $env:WATSONX_URL --type ibm_iam 2>&1 | Out-Null

Write-Host "==> Activating environment and authenticating ..." -ForegroundColor Cyan
orchestrate env activate $envName --api-key $env:WATSONX_APIKEY 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Authentication failed. Check WATSONX_URL and WATSONX_APIKEY in .env"
    exit 1
}
Write-Host "    Authenticated successfully." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 4. Import the risk_scorer tool
# ---------------------------------------------------------------------------
Write-Host "`n==> Importing risk_scorer tool ..." -ForegroundColor Cyan
orchestrate tools import --file "tools/risk_scorer.py" --kind python
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to import risk_scorer tool"; exit 1 }
Write-Host "    Done: risk_scorer" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 5. Import knowledge bases
#    Each knowledge base needs its own YAML definition file.
# ---------------------------------------------------------------------------
Write-Host "`n==> Importing knowledge bases ..." -ForegroundColor Cyan
foreach ($kb in @(
    "knowledge/grooming_warning_signs_kb.yaml",
    "knowledge/scam_patterns_kb.yaml",
    "knowledge/what_to_do_next_kb.yaml"
)) {
    Write-Host "    Importing $kb ..." -ForegroundColor DarkGray
    orchestrate knowledge-bases import --file $kb
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to import $kb"; exit 1 }
}
Write-Host "    Done: knowledge bases" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 6. Import collaborator agents FIRST (orchestrator depends on them)
# ---------------------------------------------------------------------------
Write-Host "`n==> Importing safety_agent ..." -ForegroundColor Cyan
orchestrate agents import --file "agents/safety_agent.yaml"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to import safety_agent"; exit 1 }
Write-Host "    Done: safety_agent" -ForegroundColor Green

Write-Host "`n==> Importing support_agent ..." -ForegroundColor Cyan
orchestrate agents import --file "agents/support_agent.yaml"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to import support_agent"; exit 1 }
Write-Host "    Done: support_agent" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 7. Import the orchestrator agent last
# ---------------------------------------------------------------------------
Write-Host "`n==> Importing online_safety_companion (orchestrator) ..." -ForegroundColor Cyan
orchestrate agents import --file "agents/online_safety_companion.yaml"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to import online_safety_companion"; exit 1 }
Write-Host "    Done: online_safety_companion" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 8. Verify deployment
# ---------------------------------------------------------------------------
Write-Host "`n==> Deployed agents:" -ForegroundColor Cyan
orchestrate agents list

Write-Host "`n==> Deployed tools:" -ForegroundColor Cyan
orchestrate tools list

Write-Host "`n==> Deployed knowledge bases:" -ForegroundColor Cyan
orchestrate knowledge-bases list

Write-Host "`n✅  Deployment complete!" -ForegroundColor Green
Write-Host "    Open watsonx Orchestrate and start a chat with 'Online Safety Companion'." -ForegroundColor White
