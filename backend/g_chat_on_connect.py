"""

	Author | https://github.com/davykiash

"""

import os
import json
import boto3
import botocore
from botocore.exceptions import ClientError

DYNAMODB_AWS_KEY = os.getenv('DYNAMODB_AWS_KEY')
DYNAMODB_AWS_SECRET = os.getenv('DYNAMODB_AWS_SECRET')
DYNAMODB_AWS_ENDPOINT = os.getenv('DYNAMODB_AWS_ENDPOINT')


def my_handler(event, context):
    # body = json.loads(event["body"])

    # get connection id
    connection_id = event["requestContext"]["connectionId"]
    # print(connection_id)

    # get group id
    group_id = event["queryStringParameters"]["group_id"]
    # print(record_uuid)

    # get username
    username = event["queryStringParameters"]["username"]
    # print(sender_uuid)

    # store in dynamodb connection id
    save_connection = save_new_connection_id(record_uuid, username, connection_id)
    if save_connection:

        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {"status": "success"},
            'body': "success"
        }

    else:
        return {
            'statusCode': 200,
            'body': "Connection ID Not saved"
        }


def save_new_connection_id(group_id, username, connection_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table_chat_members = dynamodb.Table('chat_members')

    try:

        response = table_chat_members.put_item(Item={'connection_id': connection_id,
                                                     'member_username ': username,
                                                     'group_id ': group_id})

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return True
