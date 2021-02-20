import os
import subprocess
import sys


# pass the url to invoke
curl_args = sys.argv[1:]
# note that "iss" (issuer) needs to have exact match to the "issuer" bucket configured in keykeeper
token = os.popen(
    "keykeeper-issue --sub ville --aud all --iss https://keykeeper-jwt-issuer-eu-west-1.s3-eu-west-1.amazonaws.com"
).read()
auth = "Authorization: " + token
print(token)
subprocess.check_call(["curl", "-H", auth] + curl_args)
