# Get the directory where the script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath

# Change to the script's directory
Set-Location $scriptPath

# Add root directory to PYTHONPATH
$env:PYTHONPATH = $rootPath

Write-Host "Running unit tests..."
python -m pytest test_lambda_chatbot.py -v 