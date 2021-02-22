import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from jwcrypto import jwk

JWKS_FILE = ".well-known/jwks.json"
OPENID_CONFIG_FILE = ".well-known/openid-configuration"


@dataclass
class KeyPair:
    public: str
    private: str


SEQ = 0


def get_some_id():
    global SEQ
    SEQ += 1
    return datetime.today().isoformat().split(".")[0].replace(":", "_") + "_%s" % SEQ


def create_pair():
    kid = get_some_id()
    jwk_key = jwk.JWK.generate(kty='RSA', size=2048, kid=kid)
    secret_key = jwk_key.export()
    public_key = jwk_key.export_public()
    return KeyPair(public_key, secret_key)


def create_jwks(keypair: KeyPair, old_jwks: Optional[str]):
    new_key_parsed = json.loads(keypair.public)

    keys_to_populate = [new_key_parsed]

    if old_jwks:
        old_keys_parsed = json.loads(old_jwks)["keys"]
        # highest kid number = newest key
        if old_keys_parsed:
            newest_old_key = max(old_keys_parsed, key=lambda k: k["kid"])
            keys_to_populate.append(newest_old_key)

    return {
        "keys": keys_to_populate
    }


def create_openid_config(full_domain_name: str):
    return {
        "issuer": f"{full_domain_name}",
        "jwks_uri": f"{full_domain_name}/.well-known/jwks.json"
    }


def domain_and_path(domain: str, path: str):
    return domain + "/" + path


def create_issuer(domain_name: str, path: str, keypair: KeyPair, old_jwks: Optional[str]):
    keys = create_jwks(keypair, old_jwks)
    return [(path + "/" + OPENID_CONFIG_FILE, json.dumps(create_openid_config(domain_and_path(domain_name,path)))),
            (path + "/" + JWKS_FILE, json.dumps(keys))]
