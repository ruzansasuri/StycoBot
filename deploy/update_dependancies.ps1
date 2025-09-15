
# Use Docker to install dependencies in a Lambda-compatible environment
Write-Host "Installing dependencies in Amazon Linux Docker container... (${PWD})"
docker run --rm `
  -v ${PWD}:/var/task `
  --entrypoint /bin/bash `
  public.ecr.aws/lambda/python:3.12 -c "pip install -r requirements.txt -t deploy/deps"
