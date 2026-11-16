<#
.SYNOPSIS
    Retail & Supply Chain Control Tower - Quick Launch Script for Windows PowerShell.
.DESCRIPTION
    Provides an interactive menu or command-line switches to initialize the database,
    run the pipeline, launch the dashboard, and run the automated test suite.
.EXAMPLE
    .\run.ps1 -Init
    .\run.ps1 -Pipeline
    .\run.ps1 -Dashboard
    .\run.ps1 -Test
#>

param(
    [switch]$Init,
    [switch]$Pipeline,
    [switch]$Dashboard,
    [switch]$Test,
    [switch]$Daemon,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectDir

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     RETAIL & SUPPLY CHAIN CONTROL TOWER (Windows PowerShell)   " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

function Show-Menu {
    Write-Host "`nPlease choose an action:" -ForegroundColor Yellow
    Write-Host "  1. Run Complete Pipeline (Refresh, KPIs, Anomalies, Prophet, What-If, Alerts)"
    Write-Host "  2. Launch Interactive Control Tower Dashboard (Streamlit)"
    Write-Host "  3. Run Automated Verification Test Suite (27 Checks)"
    Write-Host "  4. Initialize Database & Seed Synthetic Data (100 products, 10 suppliers)"
    Write-Host "  5. Start Continuous Hourly Pipeline Daemon"
    Write-Host "  6. Exit"
    Write-Host ""
    $choice = Read-Host "Enter option [1-6]"
    switch ($choice) {
        "1" { Run-Pipeline }
        "2" { Run-Dashboard }
        "3" { Run-Test }
        "4" { Run-Init }
        "5" { Run-Daemon }
        "6" { Write-Host "Exiting." -ForegroundColor Green; exit }
        Default { Write-Host "Invalid option." -ForegroundColor Red; Show-Menu }
    }
}

function Run-Init {
    Write-Host "`n[*] Initializing PostgreSQL Database schema and views..." -ForegroundColor Cyan
    python scripts\init_db.py
    Write-Host "`n[*] Generating and loading synthetic retail supply chain data..." -ForegroundColor Cyan
    python scripts\generate_data.py
    Write-Host "`n[✓] Database initialization and data seeding completed!" -ForegroundColor Green
}

function Run-Pipeline {
    Write-Host "`n[*] Executing full Control Tower pipeline..." -ForegroundColor Cyan
    python run_pipeline.py
}

function Run-Dashboard {
    Write-Host "`n[*] Launching Control Tower Dashboard at http://localhost:8501..." -ForegroundColor Cyan
    streamlit run run_dashboard.py
}

function Run-Test {
    Write-Host "`n[*] Running verification test suite..." -ForegroundColor Cyan
    python scripts\test_pipeline.py
}

function Run-Daemon {
    Write-Host "`n[*] Starting continuous hourly pipeline daemon (interval: 3600s)..." -ForegroundColor Cyan
    python run_pipeline.py --loop --interval 3600
}

# CLI Switch Handling
if ($Init) { Run-Init; exit }
if ($Pipeline) { Run-Pipeline; exit }
if ($Dashboard) { Run-Dashboard; exit }
if ($Test) { Run-Test; exit }
if ($Daemon) { Run-Daemon; exit }
if ($Help) {
    Write-Host "Usage: .\run.ps1 [-Init] [-Pipeline] [-Dashboard] [-Test] [-Daemon]" -ForegroundColor Yellow
    exit
}

# Default: Interactive Menu
Show-Menu

