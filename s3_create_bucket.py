import boto3
from utils import get_account_id


def create_bucket(s3_client):
    _bucket_name = f'datalake-lucas-{get_account_id()}'
    s3_client.create_bucket(Bucket=_bucket_name)


s3_client = boto3.client('s3')
create_bucket(s3_client)
