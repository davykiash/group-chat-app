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
URL_AWS_KEY = os.getenv('URL_AWS_KEY')
URL_AWS_SECRET = os.getenv('URL_AWS_SECRET')
URL_STAGE = os.getenv('URL_STAGE')
URL_AWS_REGION = os.getenv('URL_AWS_REGION')


def my_handler(event, context):
    # body = json.loads(event["body"])

    # get connection id
    connection_id = event["requestContext"]["connectionId"]
    # print(connection_id)

    # get connection details
    connection_details = get_connection_details(connection_id)
    if connection_details:

        # message datetime
        message_datetime = datetime.utcnow().isoformat()

        # group_id
        group_id = connection_details[0]["group_id"]

        # username
        username = connection_details[0]["username"]

		# get all messages
		all_messages = get_all_messages(group_id)

		if all_messages:

			# send all messages to the new client connection
			send_all_messages(connection_id, all_messages)
			
			return {
				'isBase64Encoded': False,
				'statusCode': 200,
				'headers': {"status": "success"},
				'body': "success"
			}

        else:
            return {
                'statusCode': 200,
                'body': "No Connection Details Found"
            }


def send_all_messages(token, json_obj):
    auth = AWSRequestsAuth(aws_access_key=URL_AWS_KEY,
                           aws_secret_access_key=URL_AWS_SECRET,
                           aws_host=URL_HOST_PUSH,
                           aws_region=URL_AWS_REGION,
                           aws_service="execute-api")

    url = 'https://' + URL_HOST_PUSH + "/" + URL_STAGE + "/%40connections/" + token.replace("=", "") + "%3D"

    req = requests.post(url, auth=auth, data=json.dumps(json_obj))

    #print(req.status_code)
    #print(req.text)


def get_all_messages(group_id, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id=DYNAMODB_AWS_KEY,
                                  aws_secret_access_key=DYNAMODB_AWS_SECRET,
                                  endpoint_url=DYNAMODB_AWS_ENDPOINT)

    table = dynamodb.Table('chat_messages')

    try:
        response = table.query(
            KeyConditionExpression=Key('group_id').eq(group_id)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Items' in response.keys():
            return response['Items']
        else:
            return None


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
