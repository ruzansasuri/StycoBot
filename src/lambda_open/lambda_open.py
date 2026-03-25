import json
import os
import boto3
from botocore.exceptions import ClientError

from libs.api.common import get_cors_headers
from libs.metrics.shared_metrics import metrics as aws_metrics_logger

BUCKET_NAME = os.environ["CV_BUCKET_NAME"]
FILE_KEY = os.environ["CV_FILE_KEY"]
URL_EXPIRY_SECONDS = 300

SUGGESTED_QUESTIONS = [
    "What stack does Ruzan work with?",
    "Most impactful projects?",
    "Is Ruzan open to new roles?",
    "How does Ruzan approach system design?",
]

s3_client = boto3.client("s3", region_name="us-east-2")
aws_metrics_logger.init("lambda_stycobot")
 
def build_cors_headers(origin: str) -> dict:
    headers, _ = get_cors_headers(origin)
    headers["Access-Control-Allow-Methods"] = "GET,OPTIONS"
    return headers
 
 
def get_suggested_questions(origin: str):
    return {
        "statusCode": 200,
        "headers": build_cors_headers(origin),
        "body": json.dumps({"questions": SUGGESTED_QUESTIONS}),
    }
 
 
def get_cv_download_url(origin: str):
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": FILE_KEY},
            ExpiresIn=URL_EXPIRY_SECONDS,
        )
        return {
            "statusCode": 200,
            "headers": build_cors_headers(origin),
            "body": json.dumps({"url": url, "expires_in": URL_EXPIRY_SECONDS}),
        }
    except ClientError as e:
        return {
            "statusCode": 500,
            "headers": build_cors_headers(origin),
            "body": json.dumps({"error": str(e)}),
        }
 
 
def lambda_handler(event, context):
    origin = event.get("headers", {}).get("origin", "")
    path = event.get("rawPath", "")
 
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": build_cors_headers(origin), "body": ""}
 
    if path.endswith("/suggested-questions"):
        return get_suggested_questions(origin)
 
    if path.endswith("/cv-download-url"):
        return get_cv_download_url(origin)
 
    return {
        "statusCode": 404,
        "headers": build_cors_headers(origin),
        "body": json.dumps({"error": "Route not found"}),
    }