
# Create deployment package for StycoBot Lambda function
Write-Host "Creating deployment package for StycoBot..."

# Create deployment directory if it doesn't exist
$deployDir = "deploy/temp"
New-Item -ItemType Directory -Force -Path $deployDir | Out-Null

# Copy dependancies from deps folder
Copy-Item deploy/deps/* $deployDir -Recurse

# Copy all required source files and folders
Copy-Item libs -Recurse -Destination $deployDir/libs
Copy-Item src/stycobot -Recurse -Destination $deployDir/stycobot
Copy-Item RAG/embeddings/embeddings.json $deployDir/stycobot/

# Remove __pycache__ folders if present
Get-ChildItem -Path $deployDir -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Create zip file
if (Test-Path deploy/StycoBot.zip) { Remove-Item deploy/StycoBot.zip -Force }
Compress-Archive -Path $deployDir\* -DestinationPath deploy/StycoBot.zip -Force

# Clean up deployment directory
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "Deployment package created: deploy/StycoBot.zip"
