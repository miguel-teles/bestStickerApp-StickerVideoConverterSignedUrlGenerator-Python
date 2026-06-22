import json

import pytest
import uuid
import os

os.environ["INPUT_BUCKET_NAME"]= 'INPUT_BUCKET_TEST'
os.environ["OUTPUT_BUCKET_NAME"]= 'OUTPUT_BUCKET_TEST'
os.environ["EXPIRATION_DURATION_SIGNED_URL_DOWNLOAD"] = str(3600)
os.environ["EXPIRATION_DURATION_SIGNED_URL_UPLOAD"] = str(3600)

from src import app

def build_body(file_name, operation):
    upload_body = json.dumps({"fileName": str(file_name), "operation": operation})

    return {
        "body": upload_body,
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }


@pytest.fixture()
def upload_body_test():
    return build_body(uuid.uuid4(), "upload")

@pytest.fixture()
def download_body_test():
    return build_body(uuid.uuid4(), "download")

@pytest.fixture()
def invalid_operation_body_test():
    return build_body(uuid.uuid4(), "invalid")

@pytest.fixture()
def null_operation_body_test():
    return build_body(uuid.uuid4(), None)


def test_upload_url(upload_body_test):
    ret = app.lambda_handler(upload_body_test, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "signedUrl" in ret["body"]
    assert "http://localhost:4566/INPUT_BUCKET_TEST/" in data["signedUrl"]
    assert "convertedFileName" in ret["body"]
    assert "out" in data.get("convertedFileName")
    assert ".webp" in data.get("convertedFileName")

def test_download_url(download_body_test):
    ret = app.lambda_handler(download_body_test, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "signedUrl" in ret["body"]
    assert "http://localhost:4566/OUTPUT_BUCKET_TEST/" in data["signedUrl"]

def test_invalid_operation(invalid_operation_body_test):
    try:
        app.lambda_handler(invalid_operation_body_test, "")
    except ValueError as e:
        assert str(e) == "Invalid operation"

def test_null_operation(null_operation_body_test):
    try:
        app.lambda_handler(null_operation_body_test, "")
    except ValueError as e:
        assert str(e) == "operation is required"