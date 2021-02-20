import json
import os
from functools import lru_cache

import boto3


# import requests

@lru_cache()
def s3client():
    return boto3.client("s3", region_name="eu-west-1",  endpoint_url='https://s3.eu-west-1.amazonaws.com')


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
    return {
        "statusCode": 200,
        "body": json.dumps({
            "get_url": get_url,
            "post_url": post_url
        }),
    }
