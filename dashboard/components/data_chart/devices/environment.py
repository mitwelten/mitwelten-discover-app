
import plotly.graph_objects as go
from dash import dcc

from dashboard.api.api_client import get_environment_data_by_id


def spider_chart(labels, keys, light_mode=True):
    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=[*keys, keys[0]],
            theta=[*labels, labels[0]],
            mode="lines",
            line_width=3,
            line_color="green",
            opacity=0.5,
            hoverinfo="skip",
            showlegend=False,
            fill="toself",
        )
    )

    fig.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        polar=dict(
            radialaxis=dict(
                # gridcolor="grey"
            ),
            angularaxis=dict(
                gridcolor="white",
                # rotation=1.3
            ),
            gridshape="linear",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin_pad=90,
        font_size=12,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h"),
    )
    return fig


def create_environment_chart(legend, trigger_id, light_mode=True):
    resp = get_environment_data_by_id(trigger_id)
    values = [resp[key] for key in legend.keys()]
    labels = [legend[key]["label"] for key in legend.keys()]

    figure = spider_chart(labels, values, light_mode)
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",
    )
    return graph

