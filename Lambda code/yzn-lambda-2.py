import json
import boto3
import urllib.parse
import re


s3 = boto3.client("s3")


def lambda_handler(event, context):

    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]

    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"]
    )

    print("Input:", key)


    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )


    transcribe_data = json.loads(
        response["Body"].read()
    )


    full_transcript = (
        transcribe_data["results"]
        ["transcripts"][0]
        ["transcript"]
    )


    output = {

        "full_transcript": full_transcript

    }


    filename = (
        key
        .split("/")[-1]
        .replace(".json","")
    )


    filename = re.sub(
        r"-transcription-\d{8}-\d{6}$",
        "",
        filename
    )


    output_key = (
        "processed/"
        + filename
        + "-processed.json"
    )


    s3.put_object(

        Bucket=bucket,

        Key=output_key,

        Body=json.dumps(
            output,
            indent=2
        ),

        ContentType="application/json"

    )


    print(
        "Created:",
        output_key
    )


    return {

        "statusCode":200,

        "body":"Lambda 2 finished"

    }
