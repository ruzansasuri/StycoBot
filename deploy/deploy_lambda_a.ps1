Write-Host "Creating deployment package for Lambda A..."

# Create deployment directory if it doesn't exist
$deployDir = "deploy/temp"
New-Item -ItemType Directory -Force -Path $deployDir | Out-Null

# No deps

# Copy all required source files and folders
Copy-Item libs -Recurse -Destination $deployDir/libs
Copy-Item src/lambda_open -Recurse -Destination $deployDir/lambda_open

# Remove __pycache__ folders if present
Get-ChildItem -Path $deployDir -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Create zip file
if (Test-Path deploy/StycoBot_A.zip) { Remove-Item deploy/StycoBot_A.zip -Force }
Compress-Archive -Path $deployDir\* -DestinationPath deploy/StycoBot_A.zip -Force

# Clean up deployment directory
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "Deployment package created: deploy/StycoBot_A.zip"
