import json
import boto3
import urllib.parse

sqs = boto3.client("sqs")
s3 = boto3.client("s3")


bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)


MODEL_ID = "amazon.nova-micro-v1:0"

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/869935078067/call-analysis-queue"

def lambda_handler(event, context):


    record = event["Records"][0]


    bucket = record["s3"]["bucket"]["name"]


    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"]
    )


    print("Analyzing:", key)



    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )


    data = json.loads(
        response["Body"].read()
    )



    full_transcript = data.get(
        "full_transcript",
        ""
    )



    prompt = f"""

You are a professional Call Center Analytics AI.

You analyze restaurant customer service calls.

You receive ONLY the complete conversation transcript.

AWS speaker labels are ignored because they may be inaccurate.


Your tasks:

1. Reconstruct the conversation.
2. Identify CUSTOMER and OPERATOR.
3. Analyze customer sentiment.
4. Identify issue and resolution.



IMPORTANT:

The transcript order is correct.

Split speakers using:

- meaning
- context
- conversation flow
- customer/operator behavior



CUSTOMER usually:

- complains
- reports problems
- asks for help
- describes personal experience
- places orders
- asks questions
- gives feedback


OPERATOR usually:

- greets customer
- apologizes
- asks questions
- provides solutions
- explains restaurant actions



IMPORTANT SPEAKER RULES:


These statements are ALWAYS OPERATOR:


"We apologize"

"We are sorry"

"Sorry for the inconvenience"

"We will prepare"

"We will replace"

"We will make a new one"

"It will be ready"

"We hope to see you again"



These statements are usually CUSTOMER:


"My food is cold"

"My order is missing"

"I received the wrong item"

"I prefer a fresh one"

"I want a refund"



CONVERSATION RULES:


Return the conversation in chronological order.


Each object represents one speaking turn.


Do NOT:

- group all CUSTOMER messages together
- group all OPERATOR messages together
- merge different speakers
- invent words
- remove words



Example:


Input:

Thank you so much. We're glad you enjoyed it.


Output:


[
{{
"role":"CUSTOMER",
"text":"Thank you so much."
}},
{{
"role":"OPERATOR",
"text":"We're glad you enjoyed it."
}}
]



CUSTOMER SENTIMENT:

Analyze ONLY customer speech.


Choose one:


POSITIVE

Customer praises the restaurant.


NEGATIVE

Customer complains or reports a problem.


NEUTRAL

Customer asks information, orders food, or checks status.



CUSTOMER CALL TYPE:


Choose one:


COMPLAINT

ORDER

INQUIRY

FEEDBACK

note about (FEEDBACK): The customer is giving opinions or reviewing the restaurant experience without requesting a solution or reporting a service issue.

ISSUE CATEGORY RULES:

- If customer_call_type is COMPLAINT, choose the most appropriate complaint category.

- If customer_call_type is ORDER, issue_category MUST be NEW_ORDER.

- If customer_call_type is INQUIRY, choose MENU_INQUIRY, ORDER_STATUS, PAYMENT, or OTHER depending on the question.

- If customer_call_type is FEEDBACK and the customer is only sharing opinions or compliments (positive or negative) without requesting a solution, issue_category MUST be NO_ISSUE.

- NEVER use NEW_ORDER unless the customer is placing an order.

- NEVER use NO_ISSUE for complaints.

ISSUE CATEGORY:

Choose only one:

COLD_FOOD

LATE_DELIVERY

MISSING_ITEMS

WRONG_ORDER

FOOD_QUALITY

PAYMENT

ORDER_STATUS

MENU_INQUIRY

NEW_ORDER

NO_ISSUE



OPERATOR ACTION:


Choose one:


REPLACED_MEAL

REHEATED_MEAL

REFUND

DISCOUNT

ORDER_UPDATED

ORDER_CONFIRMED

PROVIDED_INFORMATION

ESCALATED

NO_ACTION

OTHER



RETURN ONLY VALID JSON.

No markdown.

No explanation.



FORMAT:


{{
"conversation":[

{{
"role":"CUSTOMER",
"text":"sentence"
}},

{{
"role":"OPERATOR",
"text":"sentence"
}}

],

"customer_sentiment":"",

"customer_call_type":"",

"issue_category":"",

"resolved":true,

"operator_action":"",

"summary":""

}}



FULL TRANSCRIPT:


{full_transcript}


"""



    bedrock_response = bedrock.converse(

        modelId=MODEL_ID,


        messages=[

            {

                "role":"user",

                "content":[

                    {

                        "text":prompt

                    }

                ]

            }

        ],


        inferenceConfig={

            "maxTokens":3000,

            "temperature":0.0

        }

    )



    result = (

        bedrock_response
        ["output"]
        ["message"]
        ["content"][0]
        ["text"]

    )


    print("MODEL OUTPUT:")
    print(result)



    try:

        cleaned = result.strip()


        if cleaned.startswith("```json"):

            cleaned = cleaned.replace(
                "```json",
                "",
                1
            )


        if cleaned.endswith("```"):

            cleaned = cleaned[:-3]


        analysis = json.loads(
            cleaned.strip()
        )


    except Exception as e:

        print(
            "JSON ERROR:",
            e
        )


        analysis = {

            "raw_response": result

        }



    filename = (

        key
        .split("/")[-1]
        .replace(".json","")
        .replace("-processed","")

    )



    output_key = (

        "analysis/"
        + filename
        + "-analysis.json"

    )



    s3.put_object(

        Bucket=bucket,

        Key=output_key,


        Body=json.dumps(

            analysis,

            indent=2

        ),


        ContentType="application/json"

    )

    # Send message to SQS

    message = {
        "call_id": filename,
        "bucket": bucket,
        "analysis_key": output_key
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    print("Message sent to SQS")

    print(
        "Saved:",
        output_key
    )



    return {

        "statusCode":200,

        "body":"Lambda 3 completed"

    }
