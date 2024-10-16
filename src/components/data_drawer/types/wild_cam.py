from src.main import app
from pprint import pprint
from datetime import datetime, timezone
from dash import Output, Input, html, State, no_update, ctx, dcc
from dash import html
import dash_mantine_components as dmc
from src.api.api_client import construct_url
from src.api.api_deployment import get_wild_cam_image
from src.model.deployment import Deployment
from src.config.app_config import BACKGROUND_COLOR, PRIMARY_COLOR


STACK_SIZE = 30
RATIO = 1920/1440

def slide(object_name, ratio):
    return dmc.CarouselSlide(
            display="flex",
            maw=328 * ratio,
            children=dmc.AspectRatio(
                ratio=ratio,
                children=dmc.Anchor(
                    href=construct_url(f"tv/file/{object_name}"),
                    target="_blank",
                    children=dmc.Image(
                        h="100%",
                        fallbackSrc="https://placehold.co/600x400?text=Placeholder",
                        src=construct_url(f"tv/file/{object_name}"),
                        )
                    )
                    
                )
            )

def loader_slide(ratio):
    return dmc.CarouselSlide(
            display="flex",
            bg="#88aeae",
            maw=328 * ratio,
            style={"justifyContent":"center", "alignItems":"center"},
            children=[
                dmc.Button(
                    "Load more", 
                    id="load-more-button")
                ])

def create_wild_cam_chart(marker_data, date_range, theme):
    d = Deployment(marker_data)
    res = get_wild_cam_image(d.id, date_range["start"], date_range["end"])

    if res is None:
        return dmc.Text("No images found")

    start_time = datetime.strptime(date_range['start'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    end_time = datetime.strptime(date_range['end'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    
    filtered_data = [
        item for item in res
        if start_time <= datetime.fromisoformat(item['time']) <= end_time
    ]

    sorted_filtered_data = sorted(
        filtered_data,
        key=lambda x: datetime.fromisoformat(x['time'])
    )

    object_names = [image.get("object_name") for image in sorted_filtered_data]
    
    images = [slide(names, RATIO) for names in object_names[:STACK_SIZE]]

    if len(object_names) > STACK_SIZE:
        images.append(loader_slide(RATIO))

    if len(object_names) == 0:
        content = dmc.Text("No images found", c="dimmed")
    else:
        content = dmc.Carousel(
                children=images,
                orientation="horizontal",
                align="start",
                slideGap={ "base": "xl" },
                height="100%",
                controlsOffset="md",
                withIndicators=False,
                bg=PRIMARY_COLOR,
                w="100%",
                id="carousel-id",
                styles={"root": {"height":"100%"}}
                
                )
    return dmc.Paper(
            shadow="md",
            p="sm",
            radius="md",
            bg=BACKGROUND_COLOR,
            m="md",
            h=360,
            children=html.Div(
                style={
                    "display":"flex", 
                    "justifyContent":"center", 
                    "alignItems":"center", 
                    "height":"100%"
                    },
                children=[
                    content, 
                    dcc.Store(
                        id="carousel-store", 
                        data=dict(
                            object_names=object_names,
                            index=STACK_SIZE
                            )
                        ),
                    ],
                ),
            )


@app.callback(
        Output("carousel-id", "children"),
        Output("carousel-store", "data"),
        Input("load-more-button", "n_clicks"),
        Input("carousel-id", "children"),
        State("carousel-store", "data"),
        prevent_initial_call=True
        )

def load_more_images(_, slides, data):
    if ctx.triggered_id is None:
        return no_update

    object_names = data["object_names"]
    index = data["index"]

    # get load more button slide
    load_more_slide = slides[-1]
    slides = slides[:-1]

    new_slides = [slide(names, RATIO) for names in object_names[index:index+STACK_SIZE]]
    slides.extend(new_slides)

    # add load more button slide
    if len(object_names) > index + STACK_SIZE:
        slides.append(load_more_slide)

    data["index"] = index + STACK_SIZE

    return slides, data
