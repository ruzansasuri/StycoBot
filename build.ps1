param(
    [Parameter()]
    [ValidateSet('test', 'deploy', 'all')]
    [string]$Task = 'all'
)

# Get the directory where the script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to the script's directory
Set-Location $scriptPath

function Run-Tests {
    & ./tests/run_tests.ps1
}

function Create-DeploymentPackage {
    Write-Host "Creating deployment package for StycoBot..."
    $deployScript = Join-Path $scriptPath 'deploy/deploy.ps1'
    & $deployScript
}

# Execute tasks based on parameter
switch ($Task) {
    'test' {
        Run-Tests
    }
    'deploy' {
        Create-DeploymentPackage
    }
    default {
        Run-Tests
        if ($LASTEXITCODE -eq 0) {
            Create-DeploymentPackage
        } else {
            Write-Host "Tests failed. Deployment aborted."
            exit 1
        }
    }
} 