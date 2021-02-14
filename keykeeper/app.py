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
    return {
        "issuer": domain,
        "key_param": ssm_path
    }


def lambda_handler(event, context):
    """ Lambda handler
    """

    ret = create_new_issuer_in_s3()
    return ret
