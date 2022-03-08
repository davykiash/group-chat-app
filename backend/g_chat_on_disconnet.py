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
from aws_requests_auth.aws_auth import AWSRequestsAuth

DYNAMODB_AWS_KEY = os.getenv('DYNAMODB_AWS_KEY')
DYNAMODB_AWS_SECRET = os.getenv('DYNAMODB_AWS_SECRET')
DYNAMODB_AWS_ENDPOINT = os.getenv('DYNAMODB_AWS_ENDPOINT')
URL_HOST_PUSH = os.getenv('URL_HOST_PUSH')
URL_AWS_REGION = os.getenv('URL_AWS_REGION')
URL_AWS_KEY = os.getenv('URL_AWS_KEY')
URL_AWS_SECRET = os.getenv('URL_AWS_SECRET')
URL_STAGE = os.getenv('URL_STAGE')


def my_handler(event, context):
    # body = json.loads(event["body"])

    # get connection id
    connection_id = event["requestContext"]["connectionId"]
    # print(connection_id)

    # get record uuid and profile uuid
    connection_details = get_connection_details(connection_id)
    if connection_details:
        # message datetime
        message_datetime = datetime.utcnow().isoformat()

        # record_uuid
        group_id = connection_details[0]["group_id"]

        # profile uuid
        username = connection_details[0]["username"]

        # delete from in dynamodb record uuid and profile {both give the connection id}
        delete_connection = delete_connection_id(group_id, username, connection_id, dynamodb=None)

    else:
        return {
            'statusCode': 200,
            'body': "No Connection Details Found"
        }


def delete_connection_id(group_id, username, connection_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table_chat_members = dynamodb.Table('chat_members')

    try:

        response = table_chat_members.delete_item(Key={'connection_id': connection_id,
                                                       'member_username ': username,
														'group_id ': group_id})


    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return True


def get_connection_details(connection_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table = dynamodb.Table('chat_members')

    try:
        response = table.query(
            KeyConditionExpression=Key('connection_id').eq(connection_id)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Items' in response.keys():
            return response['Items']
        else:
            return None
