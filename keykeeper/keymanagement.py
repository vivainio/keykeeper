import json
from dataclasses import dataclass
from datetime import datetime

from jwcrypto import jwk


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


def create_jwks(keypair: KeyPair):
    parsed = json.loads(keypair.public)
    return {
        "keys": [parsed]
    }


def create_openid_config(domain_name: str):
    return {
        "issuer": f"{domain_name}",
        "jwks_uri": f"{domain_name}/.well-known/jwks.json"
    }


def create_issuer(domain_name: str, keypair: KeyPair):
    keys = create_jwks(keypair)
    return [(".well-known/openid-configuration", json.dumps(create_openid_config(domain_name))),
            (".well-known/jwks.json", json.dumps(keys))]
