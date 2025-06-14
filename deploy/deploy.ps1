# Get the directory where the script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to the script's directory
Set-Location $scriptPath

# Create deployment package for StycoBot Lambda function
Write-Host "Creating deployment package for StycoBot..."

# Create deployment directory if it doesn't exist
New-Item -ItemType Directory -Force -Path temp | Out-Null

# Copy required files to deployment directory
Copy-Item ../src/lambda_chatbot.py,../requirements.txt -Destination temp/

# Create zip file
Compress-Archive -Path temp/* -DestinationPath StycoBot.zip -Force

# Clean up deployment directory
Remove-Item -Path temp -Recurse -Force

Write-Host "Deployment package created: deploy/StycoBot.zip" 