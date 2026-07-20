import json
import boto3


dynamodb = boto3.resource("dynamodb")


apigateway = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://ueww1fczof.execute-api.us-east-1.amazonaws.com/production"
)


connections_table = dynamodb.Table(
    "DashboardConnections"
)


def lambda_handler(event, context):

    print("EVENT:")
    print(json.dumps(event))


    for record in event["Records"]:

        if record["eventName"] == "INSERT":

            new_item = record["dynamodb"]["NewImage"]


            message = {
                "type": "NEW_CALL",

                "call_id": new_item.get(
                    "call_id",
                    {}
                ).get(
                    "S",
                    ""
                ),

                "sentiment": new_item.get(
                    "customer_sentiment",
                    {}
                ).get(
                    "S",
                    "UNKNOWN"
                ),

                "call_type": new_item.get(
                    "customer_call_type",
                    {}
                ).get(
                    "S",
                    "UNKNOWN"
                ),

                "issue": new_item.get(
                    "issue_category",
                    {}
                ).get(
                    "S",
                    "OTHER"
                ),

                "action": new_item.get(
                    "operator_action",
                    {}
                ).get(
                    "S",
                    "NO_ACTION"
                ),

                "resolved": new_item.get(
                    "resolved",
                    {}
                ).get(
                    "BOOL",
                    False
                ),

                "summary": new_item.get(
                    "summary",
                    {}
                ).get(
                    "S",
                    ""
                )
            }


            print("MESSAGE:")
            print(json.dumps(message))


            connections = connections_table.scan()


            print(
                "Connections:",
                connections["Items"]
            )


            for item in connections["Items"]:

                connection_id = item["connectionId"]


                try:

                    apigateway.post_to_connection(
                        ConnectionId=connection_id,
                        Data=json.dumps(message)
                    )


                    print(
                        "Sent to:",
                        connection_id
                    )


                except Exception as e:

                    print(
                        "ERROR sending message:",
                        e
                    )


    return {
        "statusCode": 200,
        "body": "Message processed"
    }
