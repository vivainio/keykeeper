import json
import os
from functools import lru_cache
from typing import List

import boto3


# import requests

@lru_cache()
def s3client():
    return boto3.client("s3", region_name="eu-west-1", endpoint_url='https://s3.eu-west-1.amazonaws.com')


def create_get_url(bucket_name: str, path: str):
    cl = s3client()
    response = cl.generate_presigned_url('get_object',
                                         Params={
                                             'Bucket': bucket_name,
                                             'Key': path},
                                         ExpiresIn=3600)

    return response


def create_post_url(bucket_name: str, path: str):
    cl = s3client()

    # you have to use PUT method with contenttype application/octet-stream or signature fails
    response = cl.generate_presigned_url("put_object",
                                         Params={
                                             'ContentType': "application/octet-stream",
                                             'Bucket': bucket_name,
                                             'Key': path
                                         },
                                         ExpiresIn=3600
                                         )
    return response


def bucket_name():
    return os.environ["VaultBucketName"]


def handle_read(keys: List[str]):
    bucket = bucket_name()
    return {key: create_get_url(bucket_name(), key) for key in keys}


def handle_write(keys: List[str]):
    bucket = bucket_name()
    return {key: create_post_url(bucket_name(), key) for key in keys}


SYNTAX_ERROR = {
        "statusCode": 400,
        "body": 'POST request should be like {"op": "read" | "write", keys: ["path1.txt", "2/path2.txt"]}'
    }


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    bucket_name = os.environ["VaultBucketName"]
    post_url = create_post_url(bucket_name, "foo.txt")
    get_url = create_get_url(bucket_name, "foo.txt")
    parsed_body = json.loads(event["body"])
    op = parsed_body.get("op")
    keys = parsed_body.get("keys")

    if not op or not keys:
        return SYNTAX_ERROR

    if op == "read":
        res = handle_read(keys)
    elif op == "write":
        res = handle_write(keys)
    else:
        return SYNTAX_ERROR
    return {
        "statusCode": 200,
        "body": json.dumps(res),
    }
