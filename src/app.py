import json
import os

import boto3

INPUT_BUCKET_NAME = os.environ["INPUT_BUCKET_NAME"]
OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
EXPIRATION_DURATION_SIGNED_URL_UPLOAD = os.environ["EXPIRATION_DURATION_SIGNED_URL_UPLOAD"]
EXPIRATION_DURATION_SIGNED_URL_DOWNLOAD = os.environ["EXPIRATION_DURATION_SIGNED_URL_DOWNLOAD"]

def lambda_handler(event, context):
    body = event.get('body')
    if body is None:
        raise ValueError("Request body is required")

    json_content = json.loads(body)

    filename = json_content.get("fileName")
    if filename is None:
        raise ValueError("filename is required")

    operation = json_content.get('operation')
    if operation is None:
        raise ValueError("operation is required")

    # Adiciona isso se for rodar localmente
    #
    # s3 = boto3.client(
    #     "s3",
    #     endpoint_url="http://localhost:4566",
    #     aws_access_key_id="test",
    #     aws_secret_access_key="test",
    #     region_name="us-east-1"
    # )
    s3 = boto3.client(
        "s3"
    )

    out_filename = None
    if operation == "download":
        bucket_operation = 'get_object'
        bucket_name = OUTPUT_BUCKET_NAME
        expiration_duration = int(EXPIRATION_DURATION_SIGNED_URL_DOWNLOAD)
    elif operation == "upload":
        bucket_operation = 'put_object'
        bucket_name = INPUT_BUCKET_NAME
        out_filename = "out" + filename
        out_filename = out_filename.split(".")[0] + ".webp"
        expiration_duration = int(EXPIRATION_DURATION_SIGNED_URL_UPLOAD)
    else:
        raise ValueError("Invalid operation")

    signed_url = s3.generate_presigned_url(
        bucket_operation,
        Params={'Bucket': bucket_name, 'Key': filename},
        ExpiresIn=expiration_duration
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "signedUrl": signed_url,
            "convertedFileName": out_filename
        }),
    }
