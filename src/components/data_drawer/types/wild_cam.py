import json
from dash import html
from pprint import pprint
import dash_mantine_components as dmc
from pandas.io.formats.printing import justify
from src.api.api_client import construct_url
from src.api.api_deployment import get_wild_cam_image
from src.model.deployment import Deployment
from src.config.app_config import PRIMARY_COLOR

def create_wild_cam_chart(marker_data, date_range, theme):
    d = Deployment(marker_data)
    res = get_wild_cam_image(d.id, date_range["start"], date_range["end"])

    if res is None:
        return dmc.Text("No images found")

    names = [image.get("object_name") for image in res]
    ratio = 1920/1440

    def slide(image):
        return dmc.CarouselSlide(
                display="flex",
                maw=328 * ratio,
                children=dmc.AspectRatio(
                    ratio=ratio,
                    children=dmc.Image(
                        "Slide 1", 
                        src=construct_url(f"tv/file/{image}"),
                        ),
                    )
                )

    carousel = dmc.Carousel(
            [slide(name) for name in names],
            orientation="horizontal",
            align="center",
            slideGap={ "base": "xl" },
            height="auto",
            loop=True,
            controlsOffset="md",
            withIndicators=True,
            bg=PRIMARY_COLOR,
            maw=800,
            w="100%"
            )
    return dmc.Paper(
            children=html.Div(
                carousel, 
                style={"display":"flex", "justifyContent":"center", "alignItems":"center"}
                ),
            shadow="md",
            p="md",
            radius="md",
            style={"margin":"20px", "height":"360px"}
        )
    pass
