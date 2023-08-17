import json
from urllib.parse import urlencode

import requests

from dashboard.model.note import Note

DATA_API_URL = "https://data.mitwelten.org/api/v3/"


def get_deployments():
    url = construct_url("deployments")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


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
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    return None


def get_environment_data():
    url = construct_url(f"environment/entries")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_environment_data_by_id(environment_id):
    url = construct_url(f"environment/entries/{environment_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_environment_legend():
    url = construct_url(f"environment/legend")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_fake_note_by_id(note_id):
    json_note = json.loads("""
       {
		"note_id": 0,
		"node_label": "1000-0001",
		"title": "This is the Title of the Note",
		"description": "Awesome description of the note",
		"location": {
			"lat": 47.53514,
			"lon": 7.61467
		},
		"created_at": "2021-03-15T23:00:00+00:00",
		"updated_at": "2021-04-20T22:00:00+00:00",
		"creator": "Andri Wild",
		"tags": [{
			"tag_id": 135,
			"name": "FS1"
		}],
		"files": [
		    {
		        "id": 20,
		        "name": "The Book",
		        "type": "pdf",
		        "last_modified": "2021-03-15T23:00:00+00:00"
		    },
		    {
		        "id": 23,
		        "name": "Mitwelten Logo",
		        "type": "png",
		        "last_modified": "2021-03-12T23:00:00+00:00"
		    }
		    ] 

	}
    """)
    return json_note


def get_all_fake_notes():
    json_note = json.loads("""
    [
       {
		"note_id": 0,
		"node_label": "1000-0001",
		"title": "This is the Title of the Note",
		"description": "Awesome description of the note Awesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the noteAwesome description of the note",
		"location": {
			"lat": 47.53514,
			"lon": 7.61467
		},
		"created_at": "2021-03-15T23:00:00+00:00",
		"updated_at": "2021-04-20T22:00:00+00:00",
		"creator": "Andri Wild",
		"tags": [{
			"tag_id": 135,
			"name": "FS1"
		}],
		"files": [
		    {
		        "id": 20,
		        "name": "The Book",
		        "type": "pdf",
		        "last_modified": "2021-03-15T23:00:00+00:00"
		    },
		    {
		        "id": 23,
		        "name": "Mitwelten Logo",
		        "type": "png",
		        "last_modified": "2021-03-12T23:00:00+00:00"
		    }
		    ] 
	},
    {
        "note_id": 1,
        "node_label": "2000-0002",
        "title": "This is the Title of second the Note",
        "description": "Awesome description of the second note",
        "location": {
            "lat": 47.534514,
            "lon": 7.61467
        },
        "created_at": "2023-03-15T23:00:00+00:00",
        "updated_at": "2023-04-20T22:00:00+00:00",
		"creator": "Andri Wild",
        "tags": [{
            "tag_id": 128,
            "name": "z50cm"
        },
            {
                "tag_id": 135,
                "name": "FS1"
            },
            {
                "tag_id": 32,
                "name": "Villa"
            }
        ],
		"files": [
		    {
		        "id": 10,
		        "name": "Documentation",
		        "type": "pdf",
		        "last_modified": "2021-23-15T23:00:00+00:00"
		    },
		    {
		        "id": 21,
		        "name": "Foto vom Wasser",
		        "type": "png",
		        "last_modified": "2021-13-12T23:00:00+00:00"
		    }
		    ] 

    }
    ]
    """)
    return json_note


def get_note_by_id_2(note_id):
    url = construct_url(f"note/{note_id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


