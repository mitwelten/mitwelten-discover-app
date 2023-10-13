from pprint import pprint

import flask
import jwt

from dashboard.model.user import User

def get_expiration_date_from_cookies() -> int | None:
    cookies = flask.request.cookies
    if cookies is None or cookies.get("auth") is None:
        return None
    try:
        decoded_cookie = jwt.decode(cookies.get("auth"), options={"verify_signature": False})
        return decoded_cookie.get("exp")
    except Exception as e:
        print("Get expiration date info error:", e)
        return None

def get_user_from_cookies() -> User | None:
    cookies = flask.request.cookies
    try:
        decoded_cookie = jwt.decode(cookies.get("auth"), options={"verify_signature": False})
        return User(decoded_cookie)
    except Exception as e:
        print("Get user from cookie error", e)
        return None
