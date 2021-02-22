import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

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
    list_of_issuer_paths: List[str]


@lru_cache()
def get_env() -> EnvConfig:
    return EnvConfig(os.environ["IssuerDomain"], os.environ["PublicKeysBucket"],
                     os.environ["SecretKeyParameterStorePath"],
                     os.environ["ListOfIssuerPaths"].split(",")
                     )


def fetch_old_jwks(path: str):
    env = get_env()

    client = s3client()
    try:
        old_keys = client.get_object(
            Key=path + "/" + keymanagement.JWKS_FILE,
            Bucket=env.public_keys_bucket
        )
    except client.exceptions.NoSuchKey:
        # this is fine, we can start from scratch as well
        return None

    return old_keys["Body"].read()


def create_new_issuer_in_s3(path: str):
    kp = keymanagement.create_pair()
    env = get_env()
    old_keys = fetch_old_jwks(path)

    full_issuer_root = env.issuer_domain + "/" + path

    files = keymanagement.create_issuer(env.issuer_domain, path, kp, old_keys)

    for path, cont in files:
        s3client().put_object(
            Key=path,
            Body=cont,
            Bucket=env.public_keys_bucket
        )

    ssm_path = "/" + env.secret_key_parameter_store_path + "/" + path
    ssm = boto3.client("ssm")

    parameter_body = {
        "issuer": full_issuer_root,
        "key": kp.private
    }

    ssm.put_parameter(
        Name=ssm_path,
        Value=json.dumps(parameter_body),
        Type="SecureString",
        Overwrite=True,
        Description="Secret key for Keykeeper",
    )
    return {
        "issuer": full_issuer_root,
        "key_param": ssm_path
    }


def create_all_issuers():
    env = get_env()
    all = []
    for path in env.list_of_issuer_paths:
        all.append(create_new_issuer_in_s3(path))
    return all


def lambda_handler(event, context):
    """ Lambda handler
    """
    return create_all_issuers()
