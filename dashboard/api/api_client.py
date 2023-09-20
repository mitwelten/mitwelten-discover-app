import json
from urllib.parse import urlencode

import requests

from dashboard.config.api import API_URL


def construct_url(path: str, args: dict = None):
    url = f"{API_URL}{path}"
    if args:
        filtered_args = {k: v for k, v in args.items() if v is not None}
        if bool(filtered_args):
            encoded_args = urlencode(filtered_args)
            url += f"?{encoded_args}"
    return url



