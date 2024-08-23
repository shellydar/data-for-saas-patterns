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
    