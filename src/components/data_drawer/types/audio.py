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

def get_label(species_name):
    language = 'de' # en also possible
    label_key = f'label_{language}'
    for item in all_species:
        if item.get('species') == species_name:
            return item.get(label_key, "unknown")


def create_audio_chart(deployment_data, date_range, theme):

    date_str = date_range['start']
    try:
        start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        start_time = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

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
            barmode='stack',
            margin_pad=20, 
            font_size=12, 
            legend=dict(y=0.9),
        )

        df = pd.DataFrame(resp)
        df["species"] = df["species"].map(get_label)
        
        df['date'] = pd.to_datetime(df['bucket']).dt.date
        
        pivot_df = df.pivot_table(index='date', columns='species', values='count', aggfunc='sum', fill_value=0)
        
        for species in sorted(pivot_df.columns)[::-1]:
            figure.add_trace(go.Bar(
                x=pivot_df.index.astype(str),
                y=pivot_df[species],
                name=species
            ))

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
