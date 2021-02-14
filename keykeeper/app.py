import os

import boto3
import keymanagement


def create_new_issuer_in_s3():
    kp = keymanagement.create_pair()
    domain = os.environ["IssuerDomain"]
    files = keymanagement.create_issuer(domain, kp)
    bucket = os.environ["PublicKeysBucket"]
    client = boto3.client("s3")

    for path, cont in files:
        client.put_object(
            Key=path,
            Body=cont,
            Bucket=bucket
        )

    ssm_path = "/" + os.environ["SecretKeyParameterStorePath"]
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name=ssm_path,
        Value=kp.private,
        Type="SecureString",
        Overwrite=True,
        Description="Secret key for Keykeeper",
    )


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

    create_new_issuer_in_s3()
    return {
        "env": os.environ["PublicKeysBucket"]
    }
