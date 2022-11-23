import json
import urllib3

def handler(event, context):

    print('request: {}'.format(json.dumps(event)))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, Private Function Caller! You have hit {}\n'.format(event['path'])
    }