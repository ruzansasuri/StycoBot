# StycoBot - Interactive Chatbot

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

StycoBot is an interactive chatbot that can engage in conversations about food preferences, age, and favorite quotes. It's designed to be friendly and conversational, with the ability to learn about new users over time.

## Features

- Interactive command-line interface
- User authentication system
- Context-aware responses
- Support for multiple users
- Help system with available commands
- Name change functionality
- Clean and user-friendly interface

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

1. Run the chatbot:
   ```bash
   python src/chatbot.py
   ```

2. Enter your name when prompted. If you're a new user, you'll be asked to provide some information.

3. Available commands:
   - `help`: Show available commands
   - `change name`: Change your current name
   - `quit`: Exit the chatbot

4. Ask about other users by starting your message with their name:
   ```
   Ruzan what's your favorite food?
   ```

## Testing

Run the test suite to ensure everything is working correctly:
```bash
python -m pytest tests/test_chatbot.py -v
```

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

## Deployment Steps

1. **Create Deployment Package**
   - Run the PowerShell script to create the deployment package:
   ```powershell
   .\deploy\deploy.ps1
   ```
   This will create `deploy/StycoBot.zip` containing all necessary files from the `src` directory.

2. **Create a Lambda Function**
   - Go to AWS Lambda Console
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `StycoBot`
   - Runtime: Python 3.12
   - Architecture: x86_64 (cheaper than arm64)
   - Click "Create function"

3. **Configure Basic Settings**
   - Memory: 128 MB (minimum, sufficient for this chatbot)
   - Timeout: 10 seconds
   - Click "Save"

4. **Upload Code**
   - In the Lambda function page, click "Upload from" and select ".zip file"
   - Upload the `deploy/StycoBot.zip` file created in step 1

5. **Configure API Gateway**
   - In the Lambda function page, click "Add trigger"
   - Select "API Gateway"
   - Create a new API
   - Security: Open (for testing)
   - Click "Add"

6. **Test the Function**
   - Use the API Gateway endpoint URL provided
   - Send a POST request with JSON body:
   ```json
   {
     "message": "What is Ruzan's favorite food?"
   }
   ```

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

- Special thanks to the Python community for their amazing libraries and tools
- Inspired by various chatbot implementations and natural language processing techniques
- A big thank you to Cascade, the AI coding assistant, for helping to develop and refine this chatbot!

## Future Work

### Website Integration

One of the key future goals for StycoBot is to integrate it into my portfolio website, enhancing its accessibility and user engagement. This will involve:

- Adding StycoBot to my portfolio website
- Implementing real-time chat capabilities
- Creating a persistent backend to store user data
- Adding authentication and user management features
- Enhancing the chat interface with features like:
  - Message history
  - User profile management
  - Improved error handling and user feedback
  - Better context awareness in responses

The web version will allow users to interact with StycoBot directly from a browser, making it more accessible and engaging for a wider audience.
