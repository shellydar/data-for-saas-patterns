import base64
import os
import time
import requests
import urllib.request
from flask import session
from jose import jwt, jwk
from jose.utils import base64url_decode
from requests import get, post
import logging
import json
import boto3
from botocore.exceptions import ClientError

keys_map = dict()

def getData(tenant_id):
    logging.info("Getting data for tenant: " + tenant_id:)
    #logic to get data for the tenant_id


    
    
def create_temp_tenant_session(access_role_arn, session_name, tenant_id, duration_sec):
    sts = boto3.client('sts')
    assume_role_response = sts.assume_role(
        RoleArn=access_role_arn,
        DurationSeconds=duration_sec,
        RoleSessionName=session_name,
        Tags=[
            {
                'Key': 'TenantID',
                'Value': tenant_id
            }
        ]
    )
    session = boto3.Session(aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
                    aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
                    aws_session_token=assume_role_response['Credentials']['SessionToken'])
    return session    


def queryAthena(query, database, s3_output, tenant_id):
    logging.info("Querying Athena for tenant: " + tenant_id:)
    session = create_temp_tenant_session(access_role_arn, 'tenantSession', tenant_id=tenant_id, duration_sec=900)
    client=boto3.client('athena', aws_access_key_id=session.get_credentials().access_key,
                    aws_secret_access_key=session.get_credentials().secret_key,
                    aws_session_token=session.get_credentials().token)
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': s3_output,
        }
    )
def process_token(header):
    logging.debug(header)

    if str(header).__contains__('Authorization'):
        authorization = header['Authorization']
    elif str(header).__contains__('authorization'):
        authorization = header['authorization']
    else:
        raise ValueError("Missing Authorization in Header")

    if authorization:
      bearer = authorization.split()
      token = bearer[1]
    else: 
        raise ValueError("Missing Authorization in Header")  


    #get the pool id from the issuer in unverified claims to get signature key for token
    claims = jwt.get_unverified_claims(token)
    logging.debug('Claims {}'.format(claims))
    issuer = str(claims['iss'])
    lastIndex = issuer.rfind('/') + 1
    userPoolId = issuer[lastIndex:]
    logging.debug('UserPoolId: {}'.format(userPoolId))

    keys_url = issuer + '/.well-known/jwks.json'
    if keys_url in keys_map:
        keys = keys_map[keys_url]
        logging.info("Key found for keys_url: " + keys_url)
    else:
        #we store the key in map using the keys_url to reduce calls
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()
        keys = json.loads(response.decode('utf-8'))['keys']
        keys_map[keys_url] = keys
        logging.info("Add key for keys_url: " + keys_url)


    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    #print('headers {}'.format(headers))
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        raise ValueError('Public key not found in jwks.json')
        # return {
        #     "statusCode": 500,
        #     "body": json.dumps({
        #         "message": "Public key not found in jwks.json",
        #     }),
        #  }
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        raise ValueError('Signature verification failed')
    logging.debug('Signature of token successfully verified')
    
    # verify the token expiration
    if time.time() > claims['exp']: 
        raise ValueError('Token is expired')

    return token, claims
    
def lambda_handler(event, context):
    #checking for event
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info(event)
    if not str(event).__contains__('headers'):
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Missing headers",
            }),
        }

    body_ = json.loads(event['body'])
    logging.info("body: " + body_)
    try:
        start = time.time()
        #verify token and get the claims and tenant_id from the token
        token, claims = process_token(event['headers'])
        end = time.time()
        logging.debug("Verify token execution time: {}".format(end - start))
    except ClientError as err:
        logging.error("Error with token" + err)
        return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Invalid token"
                })
            }
    logging.debug('Token is valid')
    # now we can use the claims
    if not claims['custom:tenant_id']:
       logging.error('No tenant_id found')
       return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "No tenant_id attribute found in claims"
            })
        }
    else:
        tenant_id = claims['custom:tenant_id']
        logging.info("Getting data for tenant: " + tenant_id)
        getData(tenant_id)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Success",
            })
        }
        

