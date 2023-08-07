from urllib.parse import urlencode

import requests

from dashboard.config.api_config import DATA_API_URL


def construct_url(path: str, args: dict = None):
    url = f"{DATA_API_URL}{path}"
    if args:
        filtered_args = {k: v for k, v in args.items() if v is not None}
        if bool(filtered_args):
            encoded_args = urlencode(filtered_args)
            url += f"?{encoded_args}"
    return url


def get_env_timeseries(deployment_id, measurement_type, aggregation, bucket_width_m, time_from=None, time_to=None):
    url = construct_url(
        f"sensordata/{measurement_type}/{deployment_id}",
        {"aggregation": aggregation, "bucket_width_m": bucket_width_m, "from": time_from, "to": time_to})
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_pax_timeseries(deployment_id, bucket_width, time_from=None, time_to=None):
    url = construct_url(
        f"sensordata/pax/{deployment_id}",
        {"bucket_width": bucket_width, "from": time_from, "to": time_to})
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_audio_timeseries(
        taxon_id,
        deployment_id,
        confidence,
        bucket_width,
        time_from=None,
        time_to=None,
        distinctspecies=False,
):
    url = construct_url(
        f"birds/{taxon_id}/date",
        {
            "bucket_width": bucket_width,
            "conf": confidence,
            "from": time_from,
            "to": time_to,
            "distinctspecies": distinctspecies,
            "deployment_ids": deployment_id
        },
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_pollinator_timeseries(
        pollinator_class, deployment_id, confidence, bucket_width, time_from=None, time_to=None
):
    url = construct_url(
            f"pollinators/date",
            {
                "pollinator_class": pollinator_class,
                "deployment_ids": deployment_id,
                "bucket_width": bucket_width,
                "conf": confidence,
                "from": time_from,
                "to": time_to,
            },
    )
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None
