# keykeeper

Maintain AWS api gateway JWT authorizer compatible secrets, with public keys in s3 compatible bucket.

Usage:

```
$ git clone https://github.com/vivainio/keykeeper.git
$ cd keykeeper
$ sam deploy -g
```

You will get outputs like:

```

CloudFormation outputs from deployed stack
---------------------------------------------------------------------------------------------------------------------
Outputs
---------------------------------------------------------------------------------------------------------------------
Key                 CreateIssuerFunction
Description         Lambda to initiazile a new issuer with single key
Value               keykeeper-CreateIssuerFunction-19NP9SN29F419

Key                 BucketUrl
Description         Issuer url (you should point your Authorizer at this location
Value               https://keykeeper-issuer-eu-west-1.s3.amazonaws.com

Key                 SecretKeyParameterStorePath
Description         Location of the secret key in parameter store
Value               keykeeper/1

Key                 KeyKeeperIssuerBucket
Description         The issuer bucket with public keys
Value               keykeeper-issuer-eu-west-1
```

Then, when invoke the function by

```
$ aws lambda invoke --function-name keykeeper-CreateIssuerFunction-19NP9SN29F419 output.json
```

... you can observe that it has created tho following files in s3 under public bucket https://keykeeper-issuer-eu-west-1.s3.amazonaws.com

- .well-known/openid-configuration
- .well-known/keys.json

Now, you can point Api Gateway HTTP authorization JWT authorizer to the "issuer" at https://keykeeper-issuer-eu-west-1.s3.amazonaws.com

To create signed requests against this api, you need to read (--with-decrypt) the secret from parameter store and sign the JWT token with this secret:

```
$ aws ssm get-parameter --name /keykeeper/1 --with-decryption
```

```json
{
  "Parameter": {
    "Name": "/keykeeper/1",
    "Type": "SecureString",
    "Value": "{\"d\":\"s5uGl7CeLs2hPrTyh4dDToUbk-51HL1m02rBR4ATUJ2UlCEdLmBVTH6KdKRczUd4INtizj24vNDAH0jp6f5erwRys_f0qz5rSJHOQW3XBRefhbVfSR_OLVHBROPPhhIHYlXO97cd_N5bOSgonFBBdScQz4FRm0FdXNFDfWvJHdkFeyaalsXlonravAjdmyFwZtr9NNfeNk5G4nkMi2dwzsmotG6heGP-k1tGrXj1Q3BR30eNiH0jvq-L5FVlpzErvnD2y_VTTVpU9sIJLLSg9w2ZHnXoVyGsiIxZrkffZrgSx6Qp9aTxcNcJTMYF-WS105nrpzRn8op-T_LOH525rQ\",\"dp\":\"2JNlVAiKCLb2HjxwhYdpjPRyWErwu66Kh_RYI4_MHP41GeryWpjjtirVCKDZ1noVmrJ6wErUrnsBwY9tgJUxqRcfE-fFsg1FZkttWKPJfF-ToyJWfmq4LbORjvf3IRjE4AqA107VR_oNvuA5xfd35syo7ZE815JRPVr_dEIMHQs\",\"dq\":\"kHOS_ldlWc32cuOQER4t1tXWlZqjKaDbtDDz9y-bxqsqibAbOKrOUsDRQ9t_XNnazDjFt1y1Gg-QkY6PbCH-1f0wxtFnVItuY3oc0AULdPqjt_VSys8N9QK0VycS8euaqcyUTYBS3VzdkJQVyTUYkfEYYRcK7mhSoLSMuncwYvc\",\"e\":\"AQAB\",\"kid\":\"2021-02-14T12:29:57.852073_2\",\"kty\":\"RSA\",\"n\":\"xRr8ZDh9eqN87hP0r16ovg8OMqb9gYaxH4b2ZzANuHVF9EDFDQIYRmwDSelHIw_7k9W20Kwd7q3qzESKpU59JzLTo2aN8qFJY5TX8hgef_h5oRHTAitjLbn1B1kKrYIfKorezkLjmasY37bBdnWTZ9tvFbaBF-t-r9hJ92XO47ghHeNEEmUqVWvoLM597Qi0BAONTE72kqxj6ZUlWRjNFrwstx7srL1TYisLLiNSZW8VdHFSXgIf_pmW7_bQm-zGgsu9bjbfA1dXrFLX_dNryEJhuRboLntFu1SFQAL6eJKorntatT3bbWAePMIF2xjm8GJ1Ct1nFPhryBzICDedMQ\",\"p\":\"9KohfZwhNRzMFrFu8THbMKRvhg2s5pwkwsa1f4sBnTmnWOnuyb3BoBFrEMOECFS-bL2dohf7xP2Yl8U3odw9XZ7_nJ5bKvH8pzavsRGabUHDmcXa8dF01LIvjgPiOiJCyXWcClMT-vdqdocdNY4LDQQN3bRUvz9JoE4TLL09hhM\",\"q\":\"zjzGWa4SjkPOag1HTjI4bvrk0f29ciIJw_v2kIT4vvMm3Ax_XDROcXyYaVHkwLmOJA7vTxEyR95f1HM5zyosRRwsb_m-U0Hi04mdEK4Q0f79J0utnhyuW-awJHhc5Ut_sVaMt__Hagty-jnS-ouI5IgRoqvwNs5umOH2_ka4iCs\",\"qi\":\"be8mkIIajJcoh7461-N5O2VKCPXmpuOGI0aWrt07fOhqBAlsOafhJOTmE49N2ePBXTx5DmCdwKmoYcW16JgRdvkVsMV3cZi5YYdkwGPm5D_c_KmIkQw3Esx93pYhqDImJYiNCxNBp4ED53lnn0tlh3ggbkdXz4FQArXPHJRtEMc\"}",
    "Version": 3,
    "LastModifiedDate": "2021-02-14T14:29:59.488000+02:00",
    "ARN": "arn:aws:ssm:eu-west-1:512099555329:parameter/keykeeper/1"
  }
}
```

Note that the parameter path was /keykeeper/1. You can use another path by passing a different parameter to sam deploy.
