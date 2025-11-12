import os
import boto3
from botocore.config import Config
from typing import Union


# # # # # # # # # # # # # # # # # # # # # # # #
#                 API Setting                 #
# # # # # # # # # # # # # # # # # # # # # # # #
ACCOUNT_ID  = os.environ['ACCOUNT_ID']
ENDPOINT    = os.environ['ENDPOINT']
ACCESS_KEY  = os.environ["ACCESS_KEY"]
SECRET_KEY  = os.environ["SECRET_KEY"]
BUCKET     = 'temp'     # Bucket Name
KEY_PREFIX = 'images/'  # This Bucket's Folder Name

s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="auto",
    config=Config(s3={"addressing_style": "virtual"})
)

# upload one file to cloudflare r2
def upload_one(local_path: Union[str, os.PathLike]) -> tuple[bool, str, str]:
    local_path = str(local_path)
    filename = os.path.basename(local_path)
    key = f'{KEY_PREFIX}{filename}'
    s3.upload_file(local_path, BUCKET, key)
