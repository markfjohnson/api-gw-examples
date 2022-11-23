import json
import urllib3
import os

def handler(event, context):

    print('request: {}'.format(json.dumps(event)))
    url = os.environ['URL']
    url_modified = f"{url}/v1/echo"

    http = urllib3.PoolManager()
    x = http.request('GET', url)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, Private Function Caller! You have hit {}\n Response={}'.format(event['path', x])
    }