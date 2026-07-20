import boto3
import urllib.parse
import os
from datetime import datetime

transcribe = boto3.client("transcribe")


def lambda_handler(event, context):

    bucket = event["Records"][0]["s3"]["bucket"]["name"]

    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )

    print("Bucket:", bucket)
    print("Key:", key)

    file_name = os.path.basename(key)
    file_name_without_extension = os.path.splitext(file_name)[0]

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    job_name = (
        file_name_without_extension
        + "-transcription-"
        + timestamp
    )

    media_uri = f"s3://{bucket}/{key}"

    print("Job Name:", job_name)
    print("Media URI:", media_uri)

    transcribe.start_transcription_job(

        TranscriptionJobName=job_name,

        Media={
            "MediaFileUri": media_uri
        },

        MediaFormat="mp3",

        LanguageCode="en-US",

        OutputBucketName=bucket,

        OutputKey="transcripts/"

    )

    print("Started Job:", job_name)

    return {
        "status": "started",
        "job": job_name
    }
