import pytest
import json
import os
from src.lambda_chatbot import (
    validate_input,
    extract_name,
    get_user_data,
    generate_response,
    get_cors_headers,
    handle_options_request,
    lambda_handler,
    create_error_response,
    create_success_response
)

# Set test environment
os.environ['ALLOWED_ORIGINS'] = 'https://test.com'

# Test data
VALID_USER_INPUT = "What is Ruzan's favorite food?"
INVALID_USER_INPUT = "<script>alert('hack')</script>"
LONG_INPUT = "A" * 1001
EMPTY_INPUT = ""
NON_STRING_INPUT = 123

# Test events
VALID_EVENT = {
    "httpMethod": "POST",
    "headers": {
        "Origin": "https://test.com"
    },
    "body": json.dumps({"message": "What is Ruzan's favorite food?"})
}

OPTIONS_EVENT = {
    "httpMethod": "OPTIONS",
    "headers": {
        "Origin": "https://test.com"
    }
}

INVALID_JSON_EVENT = {
    "httpMethod": "POST",
    "headers": {
        "Origin": "https://test.com"
    },
    "body": "invalid json"
}

INVALID_ORIGIN_EVENT = {
    "httpMethod": "POST",
    "headers": {
        "Origin": "https://malicious.com"
    },
    "body": json.dumps({"message": "What is Ruzan's favorite food?"})
}

# Test create_error_response
def test_create_error_response():
    response = create_error_response(400, "Test error", "https://test.com")
    assert response["statusCode"] == 400
    assert "error" in json.loads(response["body"])
    assert json.loads(response["body"])["error"] == "Test error"
    assert "Access-Control-Allow-Origin" in response["headers"]

# Test create_success_response
def test_create_success_response():
    response = create_success_response("Test message", "https://test.com")
    assert response["statusCode"] == 200
    assert "message" in json.loads(response["body"])
    assert json.loads(response["body"])["message"] == "Test message"
    assert "Access-Control-Allow-Origin" in response["headers"]

# Test validate_input
def test_validate_input_valid():
    assert validate_input(VALID_USER_INPUT) is True

def test_validate_input_invalid_script():
    assert validate_input(INVALID_USER_INPUT) is False

def test_validate_input_too_long():
    assert validate_input(LONG_INPUT) is False

def test_validate_input_empty():
    assert validate_input(EMPTY_INPUT) is False

def test_validate_input_non_string():
    assert validate_input(NON_STRING_INPUT) is False

# Test extract_name
def test_extract_name_valid():
    assert extract_name("Ruzan what's your favorite food?") == "Ruzan"

def test_extract_name_invalid():
    assert extract_name("What's your favorite food?") is None

def test_extract_name_empty():
    assert extract_name("") is None

# Test get_user_data
def test_get_user_data_valid():
    user_data = get_user_data("Ruzan")
    assert user_data is not None
    assert user_data[0] == "Ruzan"
    assert user_data[1] == "34"
    assert user_data[2] == "Shrimp"
    assert user_data[3] == "Never give up"

def test_get_user_data_invalid():
    assert get_user_data("InvalidName") is None

# Test generate_response
def test_generate_response_food():
    user_data = get_user_data("Ruzan")
    response = generate_response(user_data, "food")
    assert "Shrimp" in response
    assert "Ruzan" in response

def test_generate_response_age():
    user_data = get_user_data("Ruzan")
    response = generate_response(user_data, "age")
    assert "34" in response
    assert "years young" in response

def test_generate_response_quote():
    user_data = get_user_data("Ruzan")
    response = generate_response(user_data, "quote")
    assert "Never give up" in response
    assert "Ruzan" in response

def test_generate_response_invalid():
    response = generate_response(None, "food")
    assert response == "I don't know that user."

# Test get_cors_headers
def test_get_cors_headers_allowed():
    headers = get_cors_headers("https://test.com")
    assert "Access-Control-Allow-Origin" in headers
    assert "Access-Control-Allow-Methods" in headers
    assert "Access-Control-Allow-Headers" in headers

def test_get_cors_headers_not_allowed():
    headers = get_cors_headers("https://malicious.com")
    assert headers == {}

# Test handle_options_request
def test_handle_options_request():
    response = handle_options_request(OPTIONS_EVENT)
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]
    assert response["body"] == ""

# Test lambda_handler
def test_lambda_handler_valid():
    response = lambda_handler(VALID_EVENT, None)
    assert response["statusCode"] == 200
    assert "message" in json.loads(response["body"])
    assert "Access-Control-Allow-Origin" in response["headers"]

def test_lambda_handler_options():
    response = lambda_handler(OPTIONS_EVENT, None)
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]

def test_lambda_handler_invalid_json():
    response = lambda_handler(INVALID_JSON_EVENT, None)
    assert response["statusCode"] == 400
    assert "error" in json.loads(response["body"])
    assert "Invalid request format" in json.loads(response["body"])["error"]

def test_lambda_handler_invalid_input():
    event = VALID_EVENT.copy()
    event["body"] = json.dumps({"message": INVALID_USER_INPUT})
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert "error" in json.loads(response["body"])
    assert "Invalid input" in json.loads(response["body"])["error"]

def test_lambda_handler_invalid_origin():
    response = lambda_handler(INVALID_ORIGIN_EVENT, None)
    assert response["statusCode"] == 403
    assert "error" in json.loads(response["body"])
    assert "Origin not allowed" in json.loads(response["body"])["error"] 