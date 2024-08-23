import base64
import os
import time
import requests
from flask import session
from jose import jwt
from requests import get, post
import logging
import json
from botocore.exceptions import ClientError

def getData(tenant_id):
    logging.info("Getting data for tenant: " + tenant_id:)
    #logic to get data for the tenant_id
    
    return "Data for tenant_id: " + tenant_id


def lambda_handler(event, context):
    #logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info(event)
    if not str(event).__contains__('headers'):
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Missing headers",
            }),
        }

    data = json.loads(event['body'])
    if 'message' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create the message.")
    logging.info("message: " + data['message'])
    message = data['message']
    try:
        start = time.time()
        #verify token and get the claims and tenant_id from the token
        token, claims = token_handler.process_token(event['headers'])
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

