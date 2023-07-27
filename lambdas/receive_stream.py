import json
import ast
import base64
import datetime
import uuid

import boto3

# PATHS
S3_BUCKET_RAW_DATA = "stream-raw-210570"
S3_BUCKET_REDACTED_DATA = "stream-redacted-210570"
S3_BUCKET_ANALYTICS = "stream-analytics-210570"


def decode_records(records: list[dict]) -> list:
    decoded_records = []

    for record in records:

        data = base64.b64decode( record['kinesis']['data'] ).decode('utf-8')
        data = ast.literal_eval(data)

        data['timestamp'] = str(
            datetime.datetime.fromtimestamp( record['kinesis']['approximateArrivalTimestamp'] )
        )

        data['id'] = uuid.uuid4().hex
        decoded_records.append(data)
    return decoded_records


def upload_dict_to_s3(data: dict, bucket_name: str, ):

    s3_client = boto3.client('s3')
    timestamp = datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
    
    YEAR = timestamp.year
    MONTH = timestamp.month
    DATE = timestamp.day

    FILE_KEY = f"{YEAR}/{MONTH}/{DATE}/{data['id']}.json"
    JSON_STRING = json.dumps(data)
    
    response = s3_client.put_object(
        Bucket=bucket_name,
        Key=FILE_KEY,
        Body=JSON_STRING
    )
    
    return


def lambda_handler(event, context):
    kinesis_client = boto3.client('kinesis')

    raw_records = decode_records(event['Records'])
    sentiment_records = None
    redacted_records = None

    [upload_dict_to_s3(data=current_data, bucket_name=S3_BUCKET_RAW_DATA) for current_data in raw_records]

    return {
        'statusCode': 200,
        'body': json.dumps('Records processed successfully!')
    }
