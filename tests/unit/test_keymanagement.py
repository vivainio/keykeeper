import json
from typing import Optional

from ...keykeeper import keymanagement


def test_create_jwks():
    pk = keymanagement.create_pair()
    jwkks = keymanagement.create_jwks(pk)
    print(jwkks)
    assert jwkks["keys"]


def create_and_parse_issuer(path: str, old_jwks: Optional[str]):
    kp = keymanagement.create_pair()
    issuer = keymanagement.create_issuer("https://mydomain.com", path, kp, old_jwks)
    # parse the jwks
    parsed_jwks = json.loads(issuer[1][1])
    return parsed_jwks


def test_issuer():
    # 1 should not crash if no old keys exist
    from_scratch = create_and_parse_issuer("1", None)
    assert len(from_scratch["keys"]) == 1

    old_jwks = """
        {"keys": [{"kid": "2021-02-21T18_57_12_1"}, {"kid": "2021-01-21T18_57_12_1"}]} 
    """

    from_old = create_and_parse_issuer("1", old_jwks)

    assert len(from_old["keys"]) == 2
    assert from_old["keys"][1]["kid"] == "2021-02-21T18_57_12_1"

    # once again with the keys we just got
    once_again = create_and_parse_issuer("1", json.dumps(from_old))
    assert len(once_again["keys"]) == 2


def test_many_issuers():
    ...
