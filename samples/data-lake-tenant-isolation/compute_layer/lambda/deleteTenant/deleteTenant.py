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
import boto3

def dynamoDBRecord(tenant_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('tenants')
    table.deleteItem(Key={'tenantId': tenant_id})
    logging.info(f"deleted tenant record: {tenant_id}")
    
def deletelakeFormationTag(tenant_id):
    client=boto3.client('lakeformation')
    response = client.delete_lf_tag(
        TagKey="tenant_id",
        TagValues=[
            tenant_id
            ]
    )
    logging.info(response)


def lambda_handler(event, context):
    tenant_id = None
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

    dynamoDBRecord(tenant_id)
    deletelakeFormationTag(tenant_id)
    logging.info(f"Deleted tenant: {tenant_id}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Tenant added successfully"
        })
    }
    
    