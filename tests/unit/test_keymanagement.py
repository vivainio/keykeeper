from keykeeper import keymanagement


def test_create_jwks():
    pk = keymanagement.create_pair()
    jwkks = keymanagement.create_jwks(pk)
    print(jwkks)
    assert jwkks["keys"]


def test_issuer():
    kp = keymanagement.create_pair()
    cont = keymanagement.create_issuer("mydomain.com", kp)
    print(cont)

