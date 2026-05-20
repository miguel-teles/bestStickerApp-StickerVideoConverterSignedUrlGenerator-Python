import json
import os

import boto3

BUCKET_NAME = os.environ["BUCKET_NAME"]
EXPIRATION_DURATION_SIGNED_URL = os.environ["EXPIRATION_DURATION_SIGNED_URL"]

def lambda_handler(event, context):
    body = event.get('body')
    if body is None:
        raise ValueError("Request body is required")

    key = json.loads(body).get("fileName")

    # Adiciona isso se for rodar localmente
    #
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )
    # s3 = boto3.client(
    #     "s3"
    # )

    signed_url = s3.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=EXPIRATION_DURATION_SIGNED_URL
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "signedUrl": signed_url
        }),
    }
