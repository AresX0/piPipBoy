#!/usr/bin/env pwsh
# Run pytest with project-local temp directory to avoid Windows temp cleanup permission errors
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path (Join-Path $scriptRoot "..")
$buildDir = Join-Path $projectRoot "build"
$pytestTmp = Join-Path $buildDir "pytest_tmp"
New-Item -ItemType Directory -Force -Path $pytestTmp | Out-Null
# Ensure pytest and deps are in .venv
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
# Set temporary env variables used by tempfile
$env:TEMP = $pytestTmp
$env:TMP = $pytestTmp
$env:PYTHONPATH = Join-Path $projectRoot "src"
# Run tests using basetemp for pytest as well
& $venvPython -m pytest --basetemp=$pytestTmp -q
