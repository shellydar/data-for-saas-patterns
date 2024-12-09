import base64
import os
import time
import boto3.session
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


# write a function to get data
def getData(tenant_id, query, roleARN, database, outputlocation):
    logging.info("Querying Athena for tenant: " + tenant_id)
    session= create_temp_tenant_session(access_role_arn=roleARN, session_name=tenant_id+time(), tenant_id=tenant_id, duration_sec=600)
    # query athena using the session
    client=boto3.client('athena', aws_access_key_id=session.get_credentials().access_key,
                    aws_secret_access_key=session.get_credentials().secret_key,
                    aws_session_token=session.get_credentials().token)
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': outputlocation
        }
    )
    logging.info(response)
    return response
    
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
    tenant_id = None
    query = None
    # First check if we have headers with JWT
    if 'headers' in event:
        try:
            token, claims = process_token(event['headers'])
            if 'custom:tenant_id' in claims:
                tenant_id = claims['custom:tenant_id']
                logging.info(f"Found tenant_id in JWT: {tenant_id}")
        except Exception as e:
            logging.warning(f"Could not process JWT token: {str(e)}")
    
    # If no tenant_id from JWT, check if it's directly in the event
    if not tenant_id:
        # Check different possible locations where tenantId might be
        if 'tenantId' in event:
            tenant_id = event['tenantId']
        elif 'tenant_id' in event:
            tenant_id = event['tenant_id']
        elif 'body' in event:
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                tenant_id = body.get('tenantId') or body.get('tenant_id')
            except json.JSONDecodeError:
                logging.error("Could not parse event body as JSON")
    
    if not tenant_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "No tenant_id found in request"
            })
        }
    
    if not query:
        # Check different possible locations where tenantId might be
        if 'query' in event:
            query = event['query']
        elif 'Query' in event:
            query = event['Query']
        elif 'body' in event:
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                query = body.get('query') or body.get('Query')
            except json.JSONDecodeError:
                logging.error("Could not parse event body as JSON")
    
    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "No query found in request"
            })
        }
    logging.info(f"Getting data {query} for tenant: {tenant_id}")
    # Get the role ARN and database name from environment variables
    roleARN = os.environ.get('ROLE_ARN')
    database = os.environ.get('DATABASE')
    outputlocation = os.environ.get('OUTPUT_LOCATION')
    logging.info(f"Using role ARN: {roleARN} and database: {database}")
    if not roleARN or not database:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Missing environment variables"
            })
        }
    try:
        data = getData(tenant_id, query, roleARN, database, outputlocation)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": data
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error processing request: {str(e)}"
            })
        }
        

