# Starts the backend (FastAPI/uvicorn) and frontend (Vite) dev servers, each
# in its own window, then opens the dashboard in your browser.
#
# The frontend is found by polling ports and matching the page <title> —
# Vite's console output has ANSI color codes embedded in the URL, so log
# parsing is unreliable, and the title check also skips unrelated dev
# servers that may be running on nearby ports.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$venvUvicorn = Join-Path $backendDir "venv\Scripts\uvicorn.exe"

if (-not (Test-Path $venvUvicorn)) {
    Write-Host "Backend venv not found. Set it up first:" -ForegroundColor Yellow
    Write-Host "  cd backend; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt; alembic upgrade head"
    exit 1
}
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Frontend dependencies not installed. Set them up first:" -ForegroundColor Yellow
    Write-Host "  cd frontend; npm install"
    exit 1
}

# All HTTP probing below uses curl.exe (bundled with Windows 10+), NEVER
# Invoke-WebRequest. IWR (.NET Framework) permanently breaks in this process
# once it probes a port that isn't listening yet: on this machine the first
# connect attempt to a closed local port hangs (SYN dropped, not refused),
# the aborted attempts jam the ServicePoint for that host:port (connection
# limit 2), and every later IWR call to the same URL then times out forever
# even after the server is up - measured: 240s of failures while curl.exe
# got 200 OK the whole time. This was the real cause of the long-standing
# "Backend didn't answer within 30s" message. The .exe suffix matters:
# bare "curl" in PowerShell 5.1 is an alias for Invoke-WebRequest.
function Test-Health([string]$Url) {
    $body = & curl.exe -s -m 2 $Url 2>$null
    return ($LASTEXITCODE -eq 0 -and $body -match '"ok"')
}

# uvicorn --reload spawns its actual worker via Python's multiprocessing;
# that worker can outlive the console window that launched it (observed:
# a worker from a closed window kept serving /health for days, silently
# squatting the port and making every subsequent launch collide). Detect
# an already-live backend first instead of blindly starting a duplicate.
$backendUp = $false
if (Test-Health "http://localhost:8000/health") {
    $backendUp = $true
    Write-Host "Backend already running on http://localhost:8000 - reusing it (no new window opened)." -ForegroundColor Yellow
    Write-Host "  If this is stale, close it first: Get-NetTCPConnection -LocalPort 8000 -State Listen | Stop-Process -Id { `$_.OwningProcess } -Force"
}

if (-not $backendUp) {
    Write-Host "Starting backend (FastAPI) on http://localhost:8000 ..."
    # --reload-dir app: without it, uvicorn's file watcher scans the whole
    # working directory recursively before it considers itself started -
    # including venv/, tens of thousands of files. On this OneDrive-synced
    # folder every stat() in that scan goes through the cloud-sync filter
    # driver, which measured at well over 45s to clear. Scoping the watcher
    # to app/ (a handful of .py files) is the fix, not a longer timeout.
    Start-Process -FilePath "powershell" -ArgumentList @(
        "-NoExit", "-Command",
        "Set-Location '$backendDir'; & '$venvUvicorn' app.main:app --reload --reload-dir app"
    ) -WindowStyle Normal

    Write-Host "Waiting for the backend to answer on /health ..."
    foreach ($attempt in 1..30) {
        if (Test-Health "http://localhost:8000/health") { $backendUp = $true; break }
        Start-Sleep -Seconds 1
    }
    if (-not $backendUp) {
        Write-Host "Backend didn't answer within 30s - check the backend window for errors." -ForegroundColor Yellow
    }
}

Write-Host "Starting frontend (Vite) ..."
Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$frontendDir'; npm run dev"
) -WindowStyle Normal

# Vite is configured for port 5178 but auto-increments when it's taken
Write-Host "Looking for the frontend dev server ..."
$frontendUrl = $null
foreach ($attempt in 1..30) {
    foreach ($port in 5178..5188) {
        $content = & curl.exe -s -m 2 "http://localhost:$port/" 2>$null
        if ($LASTEXITCODE -eq 0 -and $content -match "<title>Finance Tracker</title>") {
            $frontendUrl = "http://localhost:$port/"
            break
        }
    }
    if ($frontendUrl) { break }
    Start-Sleep -Seconds 1
}

if (-not $frontendUrl) {
    Write-Host "Couldn't find the frontend after 30s - check the frontend window and open its URL manually." -ForegroundColor Yellow
    exit 1
}

Write-Host "Opening $frontendUrl ..."
Start-Process $frontendUrl
