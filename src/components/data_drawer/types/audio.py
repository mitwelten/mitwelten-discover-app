import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
from dash import dcc
import dash_mantine_components as dmc
from src.model.deployment import Deployment

from src.api.api_deployment import get_bird_stacked_bar
from src.components.data_drawer.charts import create_themed_figure
from src.api.api_deployment import get_all_species

all_species = get_all_species()

def get_german_label(item):
    counter = 0
    if all_species is not None:
        species = all_species[counter].get("species")
        while item != species and counter < len(all_species):
            counter += 1
            species = all_species[counter].get("species")
        return all_species[counter].get("label_de")


def create_audio_chart(deployment_data, date_range, theme):

    start_time = datetime.strptime(date_range['start'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    end_time = datetime.strptime(date_range['end'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)

    deployment_start = datetime.fromisoformat(deployment_data['period']['start'])
    deployment_end = deployment_data['period'].get('end')
    deployment_end = datetime.fromisoformat(deployment_end) if deployment_end else None
    
    start = max(start_time, deployment_start)
    end = min(end_time, deployment_end) if deployment_end else end_time

    d = Deployment(deployment_data)
    resp = get_bird_stacked_bar(
        deployment_id=d.id,
        time_from=start,
        time_to=end,
        bucket_width="1d",
        confidence=0.9,
    )

    figure = create_themed_figure(theme)

    if resp is not None and len(resp) != 0:
        figure.update_layout(
            annotations=[{"visible":False}],
            xaxis={"visible": True},
            yaxis={"visible": True},
        )

        df = pd.DataFrame(resp)

        bars = []
        for group, dfg in df.groupby(by='species'):
            name = get_german_label(group)
            x=dfg['bucket']
            y=dfg['count']
            bars.append(go.Bar(name=name,x=x, y=y))

        timeseries = pd.bdate_range(start, end, tz="UTC", freq="D")

        figure.add_traces(bars)
        figure.add_traces(go.Bar(x=timeseries, y=[0] * len(timeseries), showlegend=False))
        figure.update_layout(
                barmode='stack', 
                margin_pad=20, 
                font_size=12, 
                legend=dict(y=0.9),
                #modebar_orientation="v"
                )

                
    graph = dcc.Graph(
        figure=figure,
        responsive=True,
        className="chart-graph",

    )
    return dmc.Paper(
            children=graph,
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        )
