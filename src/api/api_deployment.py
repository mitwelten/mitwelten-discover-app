import requests

from src.api.api_client import construct_url

def get_tags():
    url = construct_url("tags")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_deployments():
    url = construct_url("deployments")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_env_timeseries(deployment_id: int, measurement_type, aggregation, bucket_width_m, time_from=None, time_to=None):
    url = construct_url(
        f"sensordata/{measurement_type}/{deployment_id}",
        {"aggregation": aggregation, "bucket_width_m": bucket_width_m, "from": time_from, "to": time_to})
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_pax_timeseries(deployment_id: int, bucket_width: str, time_from=None, time_to=None):
    url = construct_url(
        f"sensordata/pax/{deployment_id}",
        {
            "bucket_width": bucket_width, 
            "from": time_from, 
            "to": time_to}
        )
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


def get_audio_top3(deployment_id):
    url = construct_url(f"discover/birds/top3/{deployment_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_pollinator_timeseries(
        pollinator_class, deployment_id: int, confidence: float, bucket_width: str, time_from=None, time_to=None
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
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_pollinator_heatmap( deployment_id: int, confidence, time_from=None, time_to=None):
    url = construct_url(
        f"discover/pollinators/heatmap/{deployment_id}", 
        {
            "from": time_from,
            "to": time_to,
            "conf": confidence,
        }
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_bird_stacked_bar(deployment_id: int, time_from=None, time_to=None, bucket_width="1d", confidence=0.7):
    url = construct_url(
        f"discover/birds/top/{deployment_id}", 
        {
            "bucket_width": bucket_width,
            "confidence": confidence,
            "from": time_from,
            "to": time_to,
        }
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None

def get_all_species():
    url = construct_url(f"species")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None

def get_wild_cam_image(
        deployment_id: int, 
        period_start=None, 
        period_end=None, 
        phase=None, 
        interval=None):
    url = construct_url(
        f"tv/stack-selection/", 
        {
            "deployment_id": deployment_id,
            "period_start": period_start,
            "period_end": period_end,
            "phase": phase,
            "interval": interval,
        }
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None
