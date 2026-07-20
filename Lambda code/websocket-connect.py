import boto3


dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("DashboardConnections")


def lambda_handler(event, context):

    print("CONNECT EVENT:")
    print(event)


    connection_id = event["requestContext"]["connectionId"]


    table.put_item(
        Item={
            "connectionId": connection_id
        }
    )


    print("Saved connection:", connection_id)


    return {
        "statusCode": 200,
        "body": "Connected"
    }
