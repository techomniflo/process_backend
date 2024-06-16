import boto3
from azure.storage.blob import BlobClient

def upload_to_azure(content,filepath):
    from src import AZURE_CONNECTION_STRING,AZURE_CONTAINER
    blob = BlobClient.from_connection_string(conn_str=AZURE_CONNECTION_STRING, container_name=AZURE_CONTAINER, blob_name=filepath)
    blob.upload_blob(content)
    return f"http://static.beaglenetwork.com/{AZURE_CONTAINER}/{filepath}"

def upload_to_s3(content,filename):
    from src import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
    upload_to_azure(content=content,filepath=filename)
    s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.Object('beaglebucket',filename).put(Body=content)
