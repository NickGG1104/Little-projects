from pathlib import Path
from auto_r2 import upload_one, upload_files, main_download


"""
    python -m pytest -vv --html=reports/cloudflare.html --self-contained-html
"""


class DummyS3:
    def __init__(self):
        self.calls = []

    def upload_file(self, local_path, bucket, key, ExtraArgs=None):
        # 不做真的上傳，只記錄被怎麼呼叫
        self.calls.append((local_path, bucket, key, ExtraArgs))


def test_upload_one_success(tmp_path, monkeypatch):
    f = tmp_path / 'cat.jpg'  # Pytest Temp Folder & Create File
    f.write_bytes(b'cat')     # Write Bytes Data

    dummy = DummyS3()         # auto_r2.py 中的 global s3 替換為 dummy 假物件
    monkeypatch.setattr('auto_r2.s3', dummy)

    ok, lp, key = upload_one(f)

    assert ok is True                                           # Check 'ok' is True or Not
    assert lp == str(f)                                         # Check Full File Path｜測試 API 對外的回傳值
    assert key.endswith('cat.jpg')                              # Check S3/R2 key ('images/cat.jpg')
    assert len(dummy.calls) == 1                                # Check 'upload_file' only called one time

    called_local, bucket, called_key, extra = dummy.calls[0]
    assert called_local == str(f)                               # Check Full File Path｜測試是否正確操作外部資源(R2/S3)
    assert 'max-age=31536000' in extra['CacheControl']          # 驗證快取設定是否一致


def test_upload_one_fail(tmp_path, monkeypatch):
    f = tmp_path / 'dog.jpg'
    f.write_bytes(b'dog')

    class DummyS3Fail:
        def upload_file(self, *args, **kwargs):                 # *args：接收所有「位置參數」｜**kwargs：接收所有「關鍵字參數」
            raise Exception('boom')

    monkeypatch.setattr('auto_r2.s3', DummyS3Fail())

    ok, lp, key = upload_one(f)

    assert ok is False
    assert lp == str(f)
    assert key.endswith('dog.jpg')


def test_upload_files_mix(tmp_path, monkeypatch):
    # 模擬上傳兩個檔案
    f1 = tmp_path / 'a.jpg'
    f2 = tmp_path / 'b.jpg'
    f1.write_bytes(b'1')
    f2.write_bytes(b'2')

    class DummyS3:
        def __init__(self):
            self.count = 0

        def upload_file(self, local_path, bucket, key, ExtraArgs=None):
            self.count += 1
            if self.count == 2:  # 第二次呼叫故意失敗，檢查是否正確分類
                raise Exception('fail')

    monkeypatch.setattr('auto_r2.s3', DummyS3())

    result = upload_files([f1, f2])

    assert len(result['ok']) == 1
    assert len(result['fail']) == 1


def test_main_download_calls_download_file(monkeypatch, tmp_path):
    called = []

    def fake_download_file(url, save_path):
        called.append((url, save_path))

    monkeypatch.setattr('auto_r2.download_file', fake_download_file)

    files = ['cat.jpg', 'dog.jpg']
    main_download(files)

    assert called[0][0].endswith('/images/cat.jpg')  # 驗證 url & f 是否有串在一起
    assert isinstance(called[0][1], Path)            # 驗證式普通字串還是 Path
