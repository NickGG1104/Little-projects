from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine, select, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# ---------- DB & Model ----------
class Base(DeclarativeBase):
    pass


class User(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)


# SQLite（同目錄 app.db）
engine = create_engine("sqlite:///app.db", echo=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        # 建立一個預設帳號：帳號 admin / 密碼 admin123（Demo 用，請改）
        if not s.scalar(select(User).where(User.username == "admin")):
            u = User(username="admin")
            u.set_password("admin123")
            s.add(u)
            s.commit()


# ---------- Flask App ----------
app = Flask(__name__)
app.secret_key = "change-this-secret"  # 請改成隨機長字串

login_manager = LoginManager(app)
login_manager.login_view = "login"  # 未登入訪問保護頁時導去 /login


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    with Session(engine) as s:
        return s.get(User, int(user_id))


# ---------- Routes ----------
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with Session(engine) as s:
            user = s.scalar(select(User).where(User.username == username))
            if user and user.check_password(password):
                login_user(user)
                flash("登入成功", "ok")
                next_url = request.args.get("next") or url_for("index")
                return redirect(next_url)
            else:
                flash("帳號或密碼錯誤", "err")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已登出", "ok")
    return redirect(url_for("login"))


@app.route("/password-change", methods=["GET", "POST"])
@login_required
def password_change():  # http://192.168.50.159:5000/password-change
    if request.method == "POST":
        old = request.form.get("old_password", "")
        new1 = request.form.get("new_password1", "")
        new2 = request.form.get("new_password2", "")

        if not current_user.check_password(old):
            flash("舊密碼不正確", "err")
        elif len(new1) < 6:
            flash("新密碼至少 6 碼", "err")
        elif new1 != new2:
            flash("兩次新密碼不一致", "err")
        else:
            # 更新密碼
            with Session(engine) as s:
                u = s.get(User, current_user.id)
                u.set_password(new1)
                s.commit()
            flash("密碼已更新，請重新登入", "ok")
            logout_user()
            return redirect(url_for("login"))

    return render_template("password_change.html")


# ---------- main ----------
if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
