import os, requests
import mimetypes
import boto3
from botocore.config import Config
from typing import Iterable, Union
from pathlib import Path


# # # # # # # # # # # # # # # # # # # # # # # #
#                 API Setting                 #
# # # # # # # # # # # # # # # # # # # # # # # #
ACCOUNT_ID  = os.environ.get('ACCOUNT_ID')
ENDPOINT    = os.environ.get('ENDPOINT') or (f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com' if ACCOUNT_ID else None)
ACCESS_KEY  = os.environ.get("ACCESS_KEY")
SECRET_KEY  = os.environ.get("SECRET_KEY")
BUCKET     = 'temp'     # Bucket Name
KEY_PREFIX = 'images/'  # This Bucket's Folder Name

"""bat
    set ACCOUNT_ID=xxx
    set ACCESS_KEY=xxx
    set SECRET_KEY=xxx
"""

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


# 下載檔案
def download_file(url: str, save_path: Path) -> None:
    resp = requests.get(url, stream=True)
    print('[DOWNLOAD] status:', resp.status_code)
    print('[DOWNLOAD] cf-cache-status:', resp.headers.get('cf-cache-status'))

    if resp.ok:
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):  # 每次8KB (1024=1KB)
                if chunk:
                    f.write(chunk)
        print('Saved to:', save_path.resolve())
    else:
        print('Download failed')
    print('-' * 40)


def verify_cache(url: str) -> None:
    resp = requests.get(url, stream=True)
    print('[VERIFY] status        :', resp.status_code)
    print('[VERIFY] cf-cache-status:', resp.headers.get('cf-cache-status'))
    print('[VERIFY] cache-control  :', resp.headers.get('cache-control'))
    print('[VERIFY] content-type   :', resp.headers.get('content-type'))
    print('-' * 40)


# # # # # # # # # # # # # # # # # # # # # # # #
#                    Main                     #
# # # # # # # # # # # # # # # # # # # # # # # #
def main_upload(files):
    summary = upload_files(files)
    print('\n=== Summary ===')
    print('Success:', len(summary['ok']))
    print('Failed :', len(summary['fail']))


def main_download(files):
    url = 'https://temp.nickgg.com/images/'
    path = Path('downloads')
    for f in files:
        download_file(f'{url}{f}', path / f)


def main_verify(files):
    url = 'https://temp.nickgg.com/images/'
    for f in files:
        verify_cache(f'{url}{f}')


if __name__ == '__main__':
    # main_upload([
    #     'images/cat.jpg',
    #     'images/dog.jpg',
    # ])

    # main_download([
    #     'cat.jpg',
    #     'dog.jpg'
    # ])

    main_verify([
        'cat.jpg',
        'dog.jpg'
    ])
