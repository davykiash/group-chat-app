"""
	
	Author | https://github.com/davykiash

"""

import json

def my_handler(event, context):
    
    print(event)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Does nothing. Just a holder :)')
    }
