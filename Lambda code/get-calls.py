import boto3
import json


dynamodb = boto3.resource("dynamodb")


table = dynamodb.Table(
    "CallAnalytics"
)


def lambda_handler(event, context):

    try:

        response = table.scan()

        items = response["Items"]


        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "GET"
            },
            "body": json.dumps(items)
        }


    except Exception as e:

        print(e)

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
