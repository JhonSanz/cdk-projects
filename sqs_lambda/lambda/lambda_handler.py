def handler(event, context):
    print(event)
    return { "statusCode": 200, "body": "It works :)" }