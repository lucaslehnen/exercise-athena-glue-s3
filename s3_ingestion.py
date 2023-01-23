import boto3
import os
from utils import get_bucket_name, ProgressPercentage


def ingestion(s3_client, filename):
    _bucket_name = get_bucket_name()
    _object_name = f'raw_data/enem/{os.path.basename(filename)}'
    response = s3_client.upload_file(
        filename, _bucket_name, _object_name, Callback=ProgressPercentage(filename))


s3_client = boto3.client('s3')
_file_name = os.path.abspath('./raw_data/MICRODADOS_ENEM_2020.csv')
ingestion(s3_client, _file_name)
