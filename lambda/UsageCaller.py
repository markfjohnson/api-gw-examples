import json
import urllib3
import os

def handler(event, context):

    print('request: {}'.format(json.dumps(event)))
    url = os.environ['URL']
    max_count = os.environ['CALL_COUNT']
    url_modified = f"{url}/v1/echo"

    #TODO Add the x-api-key header into the request
    http = urllib3.PoolManager()
    for n in range(0,max_count):
        x = http.request('GET', url)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, Private Function Caller! You have hit {}\n Called {}'.format(event['path', max_count])
    }