import flask
import jwt

from dashboard.model.user import User


def get_user_from_cookies():
    cookies = flask.request.cookies
    try:
        decoded_cookie = jwt.decode(cookies.get("auth"), options={"verify_signature": False})
        return User(decoded_cookie)
    except Exception as e:
        return None
