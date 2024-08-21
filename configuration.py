import os

# run locally
if os.path.exists("./.env"):
    from dotenv import load_dotenv
    load_dotenv(".env")

API_URL = "https://data.mitwelten.org/api/v3"

KC_SERVER_URL = os.environ["KC_SERVER_URL"]
KC_CLIENT_ID  = os.environ["KC_CLIENT_ID"]
KC_REALM_NAME = os.environ["KC_REALM_NAME"]
DOMAIN_NAME   = os.environ["DOMAIN_NAME"]
