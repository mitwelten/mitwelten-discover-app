
import dash_bootstrap_components as dbc

from src.config.app_config import ALERT_DURATION
from src.config.id_config import *

alert_style = dict(
    position="fixed",
    bottom=100,
    right=10,
    zIndex=999999,
    width=350
)

alert_danger = dbc.Toast(
    id=ID_ALERT_DANGER,
    header="Error",
    is_open=False,
    dismissable=True,
    duration=ALERT_DURATION,
    icon="danger",
    style=alert_style,
)


alert_warning = dbc.Toast(
    id=ID_ALERT_WARNING,
    header="Warning",
    is_open=False,
    dismissable=True,
    duration=ALERT_DURATION,
    icon="warning",
    style=alert_style,
)


alert_info = dbc.Toast(
    id=ID_ALERT_INFO,
    header="Info",
    is_open=False,
    dismissable=True,
    duration=ALERT_DURATION,
    icon="info",
    style=alert_style,
)
