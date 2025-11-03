import pytest
from sqlalchemy import create_engine
from werkzeug.security import check_password_hash

# # # # # # # # # # # # # # # # # # # # # # # # #
# import os, sys
#
# PROJECT_ROOT = os.path.dirname(__file__)  # D:\Code\Project\Flask
# if PROJECT_ROOT not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT)
# # # # # # # # # # # # # # # # # # # # # # # # #

import src.app as app_mod


@pytest.fixture(scope='function')
def test_app(monkeypatch):
    """
        1. 獨立的 Flask 測試應用，並把 app.py 內的 engine 指向記憶體 SQLite
        2. 替換 render_template 改回傳純文字
    """
    memory_engine = create_engine('sqlite+pysqlite:///:memory:', future=True)     # 用記憶體 SQLite，避免汙染本機 app.db
    monkeypatch.setattr(app_mod, 'engine', memory_engine, raising=True)     # 替換 app engine

    app_mod.Base.metadata.create_all(memory_engine)
    app_mod.init_db()

    # 測試模式
    app = app_mod.app
    app.config['TESTING'] = True
    app.secret_key = 'testing-secret'

    # mock 掉 render_template，回傳簡單字串避免找不到模板
    monkeypatch.setattr(app_mod, 'render_template', lambda name, **ctx: f'TPL:{name}', raising=True)

    with app.test_request_context():
        yield app
    memory_engine.dispose()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


def login(client, username='admin', password='admin123', follow=False):
    return client.post(
        '/login',
        data={
            'username': username,
            'password': password
        },
        follow_redirects=follow,
    )


def test_protected_requires_login(client):
    """未登入訪問 / 會被導向 /login"""
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert '/login' in resp.headers.get('Location', '')


def test_login_success(client):
    """正確帳密可登入並 302 redirect"""
    resp = login(client, 'admin', 'admin123', follow=False)
    assert resp.status_code in (302, 303)

    from urllib.parse import urlsplit
    loc = resp.headers['Location']
    path = urlsplit(loc).path
    assert path == '/'  # 登入成功預期導回 index


def test_login_failure(client):
    """錯誤密碼 -> 留在 login（200），不重導"""
    resp = login(client, 'admin', 'wrong', follow=False)
    assert resp.status_code == 200
    assert b'TPL:login.html' in resp.data


def test_logout_flow(client):
    """登入後可成功登出並重導到 /login"""
    _ = login(client)
    resp = client.get('/logout', follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert '/login' in resp.headers.get('Location', '')


def test_password_change_success(client):
    """
        修改密碼成功：
        1. 先用舊密碼登入
        2. POST /password-change
        3. 會被登出並導回 /login
        4. 用新密碼可再登入，舊密碼應失效
    """
    # 先登入
    _ = login(client, 'admin', 'admin123')

    # 修改密碼
    resp = client.post(
        '/password-change',
        data={
            'old_password': 'admin123',
            'new_password1': 'newpass888',
            'new_password2': 'newpass888',
        },
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers.get('Location', '')

    # 舊密碼應失效
    resp_old = login(client, 'admin', 'admin123', follow=False)
    assert resp_old.status_code == 200  # 留在 login

    # 新密碼可登入
    resp_new = login(client, 'admin', 'newpass888', follow=False)
    assert resp_new.status_code in (302, 303)


def test_password_change_wrong_old_password(client):
    """舊密碼錯誤 -> 仍停在表單頁（200）"""
    _ = login(client, 'admin', 'admin123')
    resp = client.post(
        '/password-change',
        data={
            'old_password': '777777',
            'new_password1': 'abc123',
            'new_password2': 'abc123',
        },
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b'TPL:password_change.html' in resp.data


def test_password_change_mismatch(client):
    """兩次新密碼不一致 -> 200"""
    _ = login(client, 'admin', 'admin123')
    resp = client.post(
        '/password-change',
        data={
            'old_password': 'admin123',
            'new_password1': 'abc12345',
            'new_password2': 'zzz99999',
        },
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b"TPL:password_change.html" in resp.data


def test_password_change_too_short(client):
    """新密碼少於 6 碼 -> 200"""
    _ = login(client, 'admin', 'admin123')
    resp = client.post(
        '/password-change',
        data={
            'old_password': 'admin123',
            'new_password1': '123',
            'new_password2': '123',
        },
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert b'TPL:password_change.html' in resp.data
