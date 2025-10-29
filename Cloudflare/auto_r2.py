import os
import mimetypes
import boto3
from botocore.config import Config
from typing import Iterable, Union


# # # # # # # # # # # # # # # # # # # # # # # #
#                 API Setting                 #
# # # # # # # # # # # # # # # # # # # # # # # #
ACCOUNT_ID = ''
ENDPOINT   = f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com'
ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET     = 'temp'     # Bucket Name
KEY_PREFIX = 'images/'  # This Bucket's Folder Name


# # # # # # # # # # # # # # # # # # # # # # # #
#                Create Client                #
# # # # # # # # # # # # # # # # # # # # # # # #
s3 = boto3.client(
    's3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="auto",
    config=Config(s3={"addressing_style": "virtual"})
)


# # # # # # # # # # # # # # # # # # # # # # # #
#                  Functions                  #
# # # # # # # # # # # # # # # # # # # # # # # #
# 上傳單一檔案；回傳 (boolean, local_path, s3_key)
def upload_one(local_path: Union[str, os.PathLike]) -> tuple[bool, str, str]:
    local_path = str(local_path)
    filename = os.path.basename(local_path)
    content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    key = f'{KEY_PREFIX}{filename}'

    try:
        s3.upload_file(
            local_path, BUCKET, key,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'public, max-age=31536000, immutable'  # 一年快取
            }
        )
        # s3.copy_object(
        #     Bucket=BUCKET,
        #     Key=key,
        #     CopySource={'Bucket': BUCKET, 'Key': key},
        #     ContentType='image/jpeg',
        #     CacheControl='public, max-age=31536000, immutable',  # 一年快取
        #     MetadataDirective='REPLACE'
        # )
        print('Uploaded:', local_path, '->', f's3://{BUCKET}/{key}')
        return True, local_path, key
    except Exception as e:
        print('Error uploading', local_path, ':', e)
        return False, local_path, key


# 多檔上傳 (list, tuple, set)
def upload_files(paths: Iterable[Union[str, os.PathLike]]) -> dict:
    result = {'ok': [], 'fail': []}
    for p in paths:
        ok, lp, key = upload_one(p)
        if ok:
            result['ok'].append(key)
        else:
            result['fail'].append((lp, key))
    return result


# # # # # # # # # # # # # # # # # # # # # # # #
#                    Main                     #
# # # # # # # # # # # # # # # # # # # # # # # #
def main(files):
    summary = upload_files(files)
    print('\n=== Summary ===')
    print('Success:', len(summary['ok']))
    print('Failed :', len(summary['fail']))


if __name__ == '__main__':
    main([
        'images/cat.jpg',
        'images/dog.jpg',
    ])
