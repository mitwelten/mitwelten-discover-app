from datetime import datetime

FIRST_DEPLOYMENT = datetime(2020, 1, 1)
FIRST_DEPLOYMENT_WEEKS_AGO = int((datetime.now().date() - FIRST_DEPLOYMENT.date()).days / 7)

# `label` represents the given `value` in weeks on the GUI
DEFAULT_DATE_RANGES = [
    {"value": f"{FIRST_DEPLOYMENT_WEEKS_AGO}", "label": "All"},
    {"value": "52", "label": "12 M"},
    {"value": "26", "label": "6 M"},
    {"value": "12", "label": "3 M"},
    {"value": "4", "label": "1 M"},
    {"value": "1", "label": "1 W"},
]

DEFAULT_TAGS = ["FS1", "FS2", "FS3"]
