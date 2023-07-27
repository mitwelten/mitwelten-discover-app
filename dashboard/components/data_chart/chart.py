from datetime import datetime, timedelta

import dash
import plotly.express as px
import plotly.graph_objects as go

from dashboard.api.api_client import get_env_timeseries, get_pax_timeseries
from dashboard.config.api_config import *
from util.validations import cleanup_timeseries


def create_env_chart(trigger_id):
    print("fetch env data - id: ", trigger_id)
    bucket_width = "1h"
    temp = get_env_timeseries(trigger_id, "temperature", "mean", bucket_width)
    hum = get_env_timeseries(trigger_id, "humidity", "mean", bucket_width)
    moi = get_env_timeseries(trigger_id, "moisture", "mean", bucket_width)

    temp = cleanup_timeseries(temp, TEMP_LOWER_BOUNDARY, TEMP_UPPER_BOUNDARY)
    hum = cleanup_timeseries(hum, HUM_LOWER_BOUNDARY, HUM_UPPER_BOUNDARY)
    moi = cleanup_timeseries(moi, MOI_LOWER_BOUNDARY, MOI_UPPER_BOUNDARY)

    new_figure = go.Figure()
    new_figure.add_trace(go.Scatter(
        x=temp['time'],
        y=temp['value'],
        name="Temperature"
    ))
    new_figure.add_trace(go.Scatter(
        x=hum['time'],
        y=hum['value'],
        yaxis='y2',
        name="Humidity"
    ))
    new_figure.add_trace(go.Scatter(
        x=moi['time'],
        y=moi['value'],
        yaxis='y3',
        name="Moisture"
    ))
    offset = 80
    new_figure.update_layout(
        xaxis=dict(domain=[0, 1]),
        yaxis=dict(
            title="Temperature",
        ),
        yaxis2=dict(
            title="Humidity",
            anchor="free",
            overlaying="y",
            shift=-offset,
        ),
        yaxis3=dict(
            title="Moisture",
            anchor="free",
            overlaying="y",
            shift=-2 * offset,
        ),
    )
    return new_figure


def create_pax_chart(trigger_id):
    print("fetch pax data - id: ", trigger_id)
    resp = get_pax_timeseries(
        deployment_id=trigger_id,
        bucket_width="1h",
        time_from=(datetime.now() - timedelta(days=1000)).isoformat(),
        time_to=datetime.now().isoformat()
    )
    new_figure = px.line(
        resp,
        x='buckets',
        y="pax",
        title=f"{dash.ctx.triggered_id['role']} - {dash.ctx.triggered_id['label']}",
    )
    return new_figure
