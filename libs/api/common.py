
import json
import logging
import os
from typing import Any, Dict

from libs.metrics.shared_metrics import metrics as aws_metrics_logger
from libs.metrics.aws_metrics import LogLevel

def create_success_response(message: str, origin: str) -> Dict[str, Any]:
    """
    Create a success response with the given message.
    
    Args:
        message: Success message to return
        origin: Request origin for CORS headers
        
    Returns:
        dict: Success response
    """
    return {
        'statusCode': 200,
        'headers': get_cors_headers(origin),
        'body': json.dumps({
            'message': message
        })
    }


def get_cors_headers(origin: str, default_allowed_origin="https://ruzansasuri.com") -> Dict[str, str]:
    """
    Get CORS headers based on the request origin.
    
    Args:
        origin: The request origin
        
    Returns:
        dict: CORS headers
    """
    # Read ALLOWED_ORIGINS from the environment variable
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', default_allowed_origin).split(',')
    aws_metrics_logger.log_event('Allowed origins', {
        'name': 'Allowed Origin list', 
        'data': allowed_origins,
        }, LogLevel.INFO)
    if origin in allowed_origins or '*' in allowed_origins:
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Max-Age': '86400'
        }, allowed_origins
    return {}, allowed_origins

def handle_options_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle OPTIONS request for CORS preflight.
    
    Args:
        event: The event data from the API Gateway
        
    Returns:
        dict: Response for OPTIONS request
    """
    origin = event.get('headers', {}).get('Origin', '')
    return {
        'statusCode': 200,
        'headers': get_cors_headers(origin),
        'body': ''
    }


def create_error_response(status_code: int, error_message: str, origin: str) -> Dict[str, Any]:
    """
    Create an error response with the given status code and message.
    
    Args:
        status_code: HTTP status code
        error_message: Error message to return
        origin: Request origin for CORS headers
        
    Returns:
        dict: Error response
    """
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps({
            'error': error_message
        })
    }