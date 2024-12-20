import time

from fastapi import FastAPI
from fastapi import Request, HTTPException, status
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
from urllib import parse
import logging

logger = logging.getLogger(__name__)

from configuration import (
    KC_SERVER_URL,
    KC_CLIENT_ID,
    KC_REALM_NAME,
    DOMAIN_NAME,
)
from src.app import app as dash_app
from src.config.app_config import REFRESH_KEY_TIME_LEFT_S

keycloak_openid = KeycloakOpenID(
    server_url=KC_SERVER_URL,
    client_id=KC_CLIENT_ID,
    realm_name=KC_REALM_NAME,
    verify=True,
)

app = FastAPI(title="Mitwelten Discover")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KC_SERVER_URL}realms/{KC_REALM_NAME}/protocol/openid-connect/auth",
    tokenUrl=f"{KC_SERVER_URL}realms/{KC_REALM_NAME}/protocol/openid-connect/token",
)
KEYCLOAK_PUBLIC_KEY = (
    "-----BEGIN PUBLIC KEY-----\n"
    + keycloak_openid.public_key()
    + "\n-----END PUBLIC KEY-----"
)


async def get_current_user(request: Request):
    # check header
    # if not valid, check cookies
    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_header = auth_header.split(" ")[1]
        try:
            return keycloak_openid.decode_token(
                auth_header,
                key=KEYCLOAK_PUBLIC_KEY,
                options={"verify_signature": True, "verify_aud": False, "exp": True},
            )
        except:
            pass
    cookie_authorization: str = request.cookies.get("auth")
    if cookie_authorization is not None:
        try:
            return keycloak_openid.decode_token(
                cookie_authorization,
                key=KEYCLOAK_PUBLIC_KEY,
                options={"verify_signature": True, "verify_aud": False, "exp": True},
            )
        except:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_refresh_token_from_cookies(request: Request):
    refresh_token: str = request.cookies.get("auth_r")
    return refresh_token


def check_time_to_refresh(user):
    s_valid = user["exp"] - int(time.time())
    return s_valid <= REFRESH_KEY_TIME_LEFT_S


def renew_token(refresh_token):
    new_token = keycloak_openid.refresh_token(refresh_token)
    return new_token.get("access_token"), new_token.get("refresh_token")


def get_auth_url(state):
    return keycloak_openid.auth_url(
        redirect_uri=f"{DOMAIN_NAME}/callback",
        scope="email",
        state=state,
    )


@app.get("/login")
def login_redirect(request: Request):
    parsed_params = parse.quote(str(request.query_params))
    return RedirectResponse(get_auth_url(f"{DOMAIN_NAME}/app/?{parsed_params}"))


@app.get("/logout")
def logout(request: Request):
    parsed_params = parse.quote(str(request.query_params))
    cookies = request.cookies
    auth_r_cookie = cookies.get("auth_r")
    response = RedirectResponse(f"{DOMAIN_NAME}/app/?{parsed_params}")
    keycloak_openid.logout(auth_r_cookie)
    response.delete_cookie("auth")
    response.delete_cookie("auth_r")
    logger.info("User logged out")
    return response


@app.get("/callback")
def callback(code, state=None):
    state = state if state is not None else f"{DOMAIN_NAME}/app"

    access_token = keycloak_openid.token(
        grant_type="authorization_code",
        code=code,
        redirect_uri=f"{DOMAIN_NAME}/callback",
    )
    response = RedirectResponse(url=state)
    response.set_cookie("auth", access_token.get("access_token"))
    response.set_cookie("auth_r", access_token.get("refresh_token"))
    return response


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    response = await call_next(request)
    if (
        not request.url.path.startswith("/login")
        and not request.url.path.startswith("/callback")
        and not request.url.path.startswith("/logout")
        and not request.url.path == "/"
    ):
        try:
            user = await get_current_user(request=request)
            # user is logged in, check if the cooky needs to be updated
            # this prevents from suddenly logged out in an activ session
            if check_time_to_refresh(user):
                refresh_token = get_refresh_token_from_cookies(request)
                auth_token, refresh_token = renew_token(refresh_token)
                response.set_cookie("auth", auth_token)
                response.set_cookie("auth_r", refresh_token)
        except:
            # user is not logged in
            pass

    return response


app.mount("/app", WSGIMiddleware(dash_app.server))


@app.get("/")
def root():
    return RedirectResponse("/app")


@app.get("/index")
def index():
    return "Hello World"
