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
    body = json.loads(event["body"])

    # get connection id
    connection_id = event["requestContext"]["connectionId"]
    print(connection_id)

    # get record uuid and profile uuid
    connection_details = get_connection_details(connection_id)
    if connection_details:

        # message datetime
        message_datetime = datetime.utcnow().isoformat()

        # record uuid
        group_id = connection_details[0]["group_id"]

        # profile uuid
        username = connection_details[0]["username"]

        # message
        message = body['message']
        # print(message)

        # save message
        save_message = save_message_to_store(group_id, username, message_datetime, message)
        if save_message:
            # get all connections with the group_id
            get_connections = get_group_connections(group_id)
            if get_connections:

                for our_items in get_connections:
                    if our_items['username'] != username:
                        json_obj_to_send = [{"chat_message": message, "datetime_message": message_datetime,
                                            "username": username}]
                        send_direct_message(our_items['connection_id'], json_obj_to_send)

                        return {
                            'statusCode': 200,
                            'body': "No User Online"
                        }
                    else:
                        return {
                            'statusCode': 200,
                            'body': "No User Online"
                        }
            else:
                return {
                    'statusCode': 200,
                    'body': "No User Online"
                }

        else:
            return {
                'statusCode': 200,
                'body': "Message not Saved"
            }

    else:
        return {
            'statusCode': 200,
            'body': "No Connection Details Found"
        }


def get_group_connections(group_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table = dynamodb.Table('chat_group_members')

    try:
        response = table.query(
            IndexName="group_id-index",
            KeyConditionExpression=Key('group_id').eq(group_id)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Items' in response.keys():
            return response['Items']
        else:
            return None


def send_direct_message(token, json_obj):
    print(token)
    auth = AWSRequestsAuth(aws_access_key=URL_AWS_KEY,
                           aws_secret_access_key=URL_AWS_SECRET,
                           aws_host=URL_HOST_PUSH,
                           aws_region=URL_AWS_REGION,
                           aws_service="execute-api")

    url = 'https://' + URL_HOST_PUSH + "/" + URL_STAGE + "/%40connections/" + token.replace("=", "") + "%3D"

    req = requests.post(url, auth=auth, data=json.dumps(json_obj))

    #print(req.status_code)
    #print(req.text)


def save_message_to_store(group_id, username, message_datetime, message, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table = dynamodb.Table('chat_messages')

    try:
        
        response = table.put_item(Item={'group_id': group_id,
                                        'date_time': message_datetime,
                                        'username': username,
                                        'chat_message': message})
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
