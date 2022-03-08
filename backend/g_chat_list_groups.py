"""

	Author | https://github.com/davykiash

"""

import os
import json
import boto3
import botocore
import requests
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

DYNAMODB_AWS_KEY = os.getenv('DYNAMODB_AWS_KEY')
DYNAMODB_AWS_SECRET = os.getenv('DYNAMODB_AWS_SECRET')
DYNAMODB_AWS_ENDPOINT = os.getenv('DYNAMODB_AWS_ENDPOINT')


def my_handler(event, context):
    # body = json.loads(event["body"])

    # store in dynamodb chat_messages user has joined
    list_of_groups = get_all_groups()
    if list_of_groups:

        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {"status": "success"},
            'body': json.dumps(list_of_groups)
        }

    else:
        return {
            'statusCode': 200,
            'body': "Connection Failed"
        }


def get_all_groups(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table = dynamodb.Table('chat_groups')

    try:
        response = table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Items' in response.keys():
            return response['Items']
        else:
            return None
