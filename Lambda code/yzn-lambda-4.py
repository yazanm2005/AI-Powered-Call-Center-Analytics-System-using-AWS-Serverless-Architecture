import json
import boto3


s3 = boto3.client("s3")

dynamodb = boto3.resource(
    "dynamodb"
)


table = dynamodb.Table(
    "CallAnalytics"
)



def lambda_handler(event, context):


    for record in event["Records"]:


        message = json.loads(
            record["body"]
        )


        bucket = message["bucket"]

        analysis_key = message["analysis_key"]

        call_id = message["call_id"]



        print(
            "Processing:",
            call_id
        )



        response = s3.get_object(

            Bucket=bucket,

            Key=analysis_key

        )


        analysis = json.loads(

            response["Body"].read()

        )



        item = {

            "call_id": call_id,

            "customer_sentiment":
                analysis.get(
                    "customer_sentiment"
                ),


            "customer_call_type":
                analysis.get(
                    "customer_call_type"
                ),


            "issue_category":
                analysis.get(
                    "issue_category"
                ),


            "resolved":
                analysis.get(
                    "resolved"
                ),


            "operator_action":
                analysis.get(
                    "operator_action"
                ),


            "summary":
                analysis.get(
                    "summary"
                ),


            "conversation":
                analysis.get(
                    "conversation"
                )

        }



        table.put_item(

            Item=item

        )



        print(
            "Saved to DynamoDB:",
            call_id
        )



    return {


        "statusCode":200,

        "body":"Lambda 4 completed"

    }
