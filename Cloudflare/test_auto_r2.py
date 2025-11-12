from pathlib import Path
from auto_r2 import upload_one

class DummyS3:
    def __init__(self):
        self.calls = []

    def upload_file(self, local_path, bucket, key, ExtraArgs=None):
        pass


def test_upload_one_success(tmp_path, monkeypatch):
    f = tmp_path / 'cat.jpg'  # Pytest Temp Folder & Create File
    f.write_bytes(b'cat')     # Write Bytes Data

    dummy = DummyS3()         # auto_r2.py 中的 global s3 替換為 dummy 假物件
    monkeypatch.setattr('auto_r2.s3', dummy)

    upload_one(f)


@pytest.skip(reason="Need real Cloudflare R2 account info")
def test_real_cloudflare_upload():
    # 上傳
    # 下載
    # 驗證檔案一致
    pass


# 下載檔案
def download_file(url: str, save_path: Path) -> None:
    resp = requests.get(url, stream=True)

    if resp.ok:
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):  # 每次8KB (1024=1KB)
                if chunk:
                    f.write(chunk)
        print('Saved to:', save_path.resolve())
    else:
        print('Download failed')
    print('-' * 40)
