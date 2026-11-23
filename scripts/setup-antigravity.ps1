<#
.SYNOPSIS
    Automated setup script for Reverse Engineer Anything (REA) in Google Antigravity.
.DESCRIPTION
    Checks Node.js, Python, installs/updates dependencies, and registers the REA plugin in Antigravity.
#>

param(
    [switch]$InstallGlobal = $true,
    [switch]$UpdateNode = $false
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Reverse Engineer Anything (REA) - Antigravity Setup      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    $pyVer = & python --version
    Write-Host "  Found Python: $pyVer" -ForegroundColor Green
} else {
    Write-Warning "  Python not found on PATH. Please install Python 3.8+."
}

# 2. Check Node.js
Write-Host "[2/4] Checking Node.js environment..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    $nodeVer = & node -v
    Write-Host "  Found Node: $nodeVer" -ForegroundColor Green
} else {
    Write-Warning "  Node.js not found on PATH."
}

# 3. Test rea_helper.py
Write-Host "[3/4] Verifying REA Companion Helper..." -ForegroundColor Yellow
$testOutput = & python scripts/rea_helper.py --help
if ($LASTEXITCODE -eq 0) {
    Write-Host "  REA Companion script verified successfully." -ForegroundColor Green
} else {
    Write-Error "  Failed to execute scripts/rea_helper.py."
}

# 4. Global Antigravity Plugin Setup
if ($InstallGlobal) {
    Write-Host "[4/4] Registering Global Antigravity Plugin..." -ForegroundColor Yellow
    $globalPluginsDir = "$HOME\.gemini\config\plugins\reverse-engineer-anything"
    New-Item -ItemType Directory -Path $globalPluginsDir -Force | Out-Null
    Copy-Item -Path ".agents\plugin.json" -Destination "$globalPluginsDir\plugin.json" -Force
    Copy-Item -Path ".agents\mcp_config.json" -Destination "$globalPluginsDir\mcp_config.json" -Force
    Copy-Item -Path ".agents\skills" -Destination $globalPluginsDir -Recurse -Force
    Copy-Item -Path ".agents\rules" -Destination $globalPluginsDir -Recurse -Force
    Copy-Item -Path ".agents\agents" -Destination $globalPluginsDir -Recurse -Force
    Write-Host "  Successfully installed plugin to $globalPluginsDir!" -ForegroundColor Green
}

Write-Host "`n Setup Complete! You can now use REA with Gemini AI in Antigravity." -ForegroundColor Green
