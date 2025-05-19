import requests
import pandas as pd
import io
import boto3
from azure.storage.blob import BlobServiceClient

BEA_API = "https://apps.bea.gov/api/data/"

LINECODES = [50, 110, 240]
TABLE_NAME = "CAINC4"


def download_bea(api_key: str, year: str = "ALL") -> pd.DataFrame:
    frames = []
    for line in LINECODES:
        params = {
            "UserID": api_key,
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": TABLE_NAME,
            "LineCode": line,
            "GeoFIPS": "COUNTY",
            "Year": year,
            "ResultFormat": "JSON",
        }
        r = requests.get(BEA_API, params=params)
        r.raise_for_status()
        data = r.json()["BEAAPI"]["Results"]["Data"]
        df = pd.DataFrame(data)
        df["LineCode"] = line
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def save_df_to_s3(df, bucket_name, key, aws_access_key_id, aws_secret_access_key, region_name="us-east-1"):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())
    print(f"Uploaded DataFrame to s3://{bucket_name}/{key}")


def save_df_to_azure_blob(df, container_name, blob_name, connection_string):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container = blob_service.get_container_client(container_name)
    container.upload_blob(name=blob_name, data=buffer, overwrite=True)
    print(f"Uploaded DataFrame to azure://{container_name}/{blob_name}")
