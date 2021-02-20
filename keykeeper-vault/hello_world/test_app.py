import json
import os

from .app import create_get_url, lambda_handler


def test_create_get_url():
    print(create_get_url("keykeeper-vault-1", "/foo.txt"))


def test_lambda_handler():
    os.environ["VaultBucketName"] = "keykeeper-vault-1"
    postbody_json = {
        "op": "read",
        "keys": ["foo.txt", "2/bar.txt"]
    }
    event = {
        "body": json.dumps(postbody_json)
    }
    print(lambda_handler(event, None))
