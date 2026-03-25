
# Create deployment package for StycoBot Lambda function
Write-Host "Creating deployment package for StycoBot..."

& "$PSScriptRoot\deploy_lambda_a.ps1" 
& "$PSScriptRoot\deploy_lambda_b.ps1"

Write-Host "All deployment packages created"
