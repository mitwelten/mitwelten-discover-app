from dash import html

from src.api.api_files import get_file_url
from src.components.media.player import audio_player
from src.model.file import File
from src.config.id_config import *

def slideshow(theme, files: list[File]): 
    light_mode = theme["colorScheme"] == "light"
    background = "#F2F2F2" if light_mode else "#373A40"

    file = files[0]

    slideshow_buttons = []
    if len(files) > 1:
        slideshow_buttons = [
                html.Button("❮", id=ID_SLIDESHOW_BTN_LEFT, className="slide-btn slide-btn-left"), 
                html.Button("❯", id=ID_SLIDESHOW_BTN_RIGHT, className="slide-btn slide-btn-right"), 
                ]

    url = get_file_url(file.object_name)
    image_src = ""
    audio_src = ""
    if file.type.startswith("image/"):
        image_src = url
    else:
        audio_src = url

    return [html.Div(
            children=[
                html.Img(id=ID_SLIDESHOW_IMAGE, className="cropped-ofp", src=image_src),
                audio_player(id=ID_AUDIO_PLAYER, light_mode=light_mode, src=audio_src),
        ],
            className="image-box", 
            style={"background": background}
        ),
            *slideshow_buttons
    ]
