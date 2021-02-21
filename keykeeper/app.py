import os
from dataclasses import dataclass
from functools import lru_cache

import boto3
import keymanagement


@lru_cache()
def s3client():
    client = boto3.client("s3")
    return client


@dataclass
class EnvConfig:
    issuer_domain: str
    public_keys_bucket: str
    secret_key_parameter_store_path: str


@lru_cache()
def get_env() -> EnvConfig:
    return EnvConfig(os.environ["IssuerDomain"], os.environ["PublicKeysBucket"],
                     os.environ["SecretKeyParameterStorePath"])


def fetch_old_jwks():
    env = get_env()

    client = s3client()
    try:
        old_keys = client.get_object(
            Key=keymanagement.JWKS_FILE,
            Bucket=env.public_keys_bucket
        )
    except client.exceptions.NoSuchKey:
        # this is fine, we can start from scratch as well
        return None

    return old_keys["Body"].read()


def create_new_issuer_in_s3():
    kp = keymanagement.create_pair()
    env = get_env()
    old_keys = fetch_old_jwks()
    files = keymanagement.create_issuer(env.issuer_domain, kp, old_keys)

    for path, cont in files:
        s3client().put_object(
            Key=path,
            Body=cont,
            Bucket=env.public_keys_bucket
        )

    ssm_path = "/" + env.secret_key_parameter_store_path
    ssm = boto3.client("ssm")
    ssm.put_parameter(
        Name=ssm_path,
        Value=kp.private,
        Type="SecureString",
        Overwrite=True,
        Description="Secret key for Keykeeper",
    )
    return {
        "issuer": env.issuer_domain,
        "key_param": ssm_path
    }


def lambda_handler(event, context):
    """ Lambda handler
    """

    ret = create_new_issuer_in_s3()
    return ret
