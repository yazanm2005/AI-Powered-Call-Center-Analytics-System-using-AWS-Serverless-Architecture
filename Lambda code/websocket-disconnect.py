import boto3


dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("DashboardConnections")


def lambda_handler(event, context):

    print("DISCONNECT EVENT:")
    print(event)


    connection_id = event["requestContext"]["connectionId"]


    table.delete_item(
        Key={
            "connectionId": connection_id
        }
    )


    print("Removed connection:", connection_id)


    return {
        "statusCode": 200,
        "body": "Disconnected"
    }
