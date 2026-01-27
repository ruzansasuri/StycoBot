# StycoBot - Interactive Chatbot

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

StycoBot is an interactive chatbot that can engage in conversations about Ruzan Sasuri's professional experience. It's designed to be friendly and conversational, with a RAG system to update the knowledge base.

## Getting Started

### Prerequisites

- Python 3.12 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DBAgent.git
   cd DBAgent
   ```

2. Install dependencies:
   ```bash
   pip install pytest
   ```

### Usage

1. Make sure to create a new AWS Lambda instance.
2. Run deploy/deploy.ps1 to create StycoBot.zip
3. Uploade StycoBot.zip to AWS Lambda code.
4. Set environment variables:
   - ALLOWED_ORIGINS=https://ruzansasuri.com(or any implementation of a chat window you want.)
   - ENVIRONMENT=prod
   - METRICS_SQS_QUEUE_URL=`Metrics Queue URL for cloud watch metrics`
   - OPENAI_API_KEY=`Set to an OPENAI key from your account`


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

# AWS Lambda Deployment Guide

This guide will help you deploy the StycoBot chatbot to AWS Lambda while keeping costs minimal.

## Prerequisites

1. An AWS account
2. AWS CLI installed and configured
3. Python 3.12 or later


## Cost Optimization

The setup above is optimized for minimal costs:
- 128 MB memory (minimum)
- x86_64 architecture (cheaper than arm64)
- No external dependencies
- In-memory data storage
- Short timeout

## Monitoring

Monitor your usage in the AWS Lambda Console to ensure you stay within the free tier limits.

## Security Note

For production use, consider:
1. Adding proper authentication
2. Using AWS Secrets Manager for sensitive data
3. Implementing rate limiting
4. Using HTTPS only

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the Python community for their amazing libraries and tools.
- Inspired by various chatbot implementations and natural language processing techniques.
- Possible due to the accessible OPENAI's chatgpt API.
- Claude, the AI coding assistant, helping to quickly develop and refine this chatbot.
