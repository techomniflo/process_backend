import boto3

def upload_to_s3(content,filename):
    from src import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
    s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    s3.Object('beaglebucket',filename).put(Body=content)

    