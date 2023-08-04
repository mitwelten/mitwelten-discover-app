import time
from datetime import datetime, timedelta

import dash
import plotly.express as px
import plotly.graph_objects as go

import dash_mantine_components as dmc
from dash import dcc

from dashboard.api.api_client import get_env_timeseries, get_pax_timeseries
from dashboard.config.api_config import *
from util.validations import cleanup_timeseries


def create_figure_from_timeseries(series, light_mode, x_label="time", y_label="value"):
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    figure.add_trace(go.Scatter(
        x=series[x_label],
        y=series[y_label],
    ))
    return figure
