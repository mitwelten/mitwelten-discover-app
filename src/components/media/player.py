import dash_html_components as html
import dash_mantine_components as dmc
from dash import Output, Input, State
from dash_extensions import EventListener
from src.main import app

from src.config.id_config import *
from dash_iconify import DashIconify
from dash import ClientsideFunction, html, ctx

play_icon = "material-symbols:play-arrow-rounded"
pause_icon = "material-symbols:pause-rounded"

ID_AUDIO_TIME_PROGRESS = "id-audio-time-progress"
ID_AUDIO_STOP_BTN  = "id-audio-stop-button"
ID_AUDIO_PLAY_PAUSE_BTN = "id-audio-play-pause-button"
ID_AUDIO_MUTE_BTN  = "id-audio-mute-button"
ID_AUDIO_PLAY_PAUSE_ICON = "id-audio-play-pause-icon"
ID_AUDIO_STOP_ICON = "id-audio-stop-icon"
ID_AUDIO_MUTE_ICON = "id-audio-mute-icon"
ID_EVENT_LISTENER = "id-event-listener"

def audio_player(id: str):
    return dmc.Stack(
        id=id,
        className="audio-player",
        style={"display": "none"},
        children=[
            EventListener(
                 html.Audio(id=ID_AUDIO),
                 events = [{"event": "timeupdate"}, {"event": "loadeddata"}],
                 id=ID_EVENT_LISTENER
            ),
            dmc.Group([
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:stop-rounded", width=50),
                        id=ID_AUDIO_STOP_BTN,
                        variant="transparent",
                        style={"width": "35px", "height": "35px"}
                    ),
                html.Div(
                    dmc.ActionIcon(
                        DashIconify(icon=play_icon, width=100, id=ID_AUDIO_PLAY_PAUSE_ICON),
                        id=ID_AUDIO_PLAY_PAUSE_BTN,
                        variant="transparent",
                        style={"width": "75px", "height": "75px"}
                    ),
                    style={
                        "display": "flex",
                        "background": "white",
                        "width": "80px",
                        "height": "80px",
                        "border-radius": "50%",
                        "justify-content": "center",
                        "align-items": "center"
                    }
                ),
                    dmc.ActionIcon(
                        DashIconify(id=ID_AUDIO_MUTE_ICON, icon="material-symbols:no-sound-rounded", width=50),
                        id=ID_AUDIO_MUTE_BTN,
                        variant="transparent",
                        style={"width": "35px", "height": "35px"}
                    ),
            ]
            ),
            dmc.Text("-:- / -:-", id=ID_AUDIO_TIME_PROGRESS)
        ])

app.clientside_callback(
    ClientsideFunction(namespace="audio", function_name="progress"),
    Output(ID_AUDIO_TIME_PROGRESS, "children", allow_duplicate=True),
    Input(ID_EVENT_LISTENER, "n_events"),
    State(ID_AUDIO, "id"),
    prevent_initial_call=True
)

@app.callback(
    Output(ID_AUDIO_MUTE_ICON, "icon"),
    Input(ID_AUDIO_MUTE_BTN, "n_clicks"),
    State(ID_AUDIO_MUTE_ICON, "icon"),
    prevent_initial_call=True
)

def toggle_no_sound_icon(_, icon):
    if "no" in icon:
        return "material-symbols:volume-up-rounded"
    return "material-symbols:no-sound-rounded"

app.clientside_callback(
    ClientsideFunction(namespace="audio", function_name="noSound"),
    Output(ID_AUDIO_MUTE_BTN, "n_clicks"),
    Input(ID_AUDIO_MUTE_BTN, "n_clicks"),
    State(ID_AUDIO, "id"),
    prevent_initial_call=True
)

app.clientside_callback(
    ClientsideFunction(namespace="audio", function_name="stop"),
    Output(ID_AUDIO_TIME_PROGRESS, "children", allow_duplicate=True),
    Input(ID_AUDIO_STOP_BTN, "n_clicks"),
    State(ID_AUDIO, "id"),
    prevent_initial_call=True
)

app.clientside_callback(
    ClientsideFunction(namespace="audio", function_name="playOrPause"),
    Output(ID_AUDIO_PLAY_PAUSE_BTN, "n_clicks", allow_duplicate=True),
    Input(ID_AUDIO_PLAY_PAUSE_BTN, "n_clicks"),
    State(ID_AUDIO, "id"),
    prevent_initial_call=True
)

app.clientside_callback(
    ClientsideFunction(namespace="audio", function_name="pause"),
    Output(ID_AUDIO, "id", allow_duplicate=True),
    Input(ID_SLIDESHOW_BTN_LEFT, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_RIGHT, "n_clicks"),
    State(ID_AUDIO, "id"),
    prevent_initial_call=True
)

@app.callback(
    Output(ID_AUDIO_PLAY_PAUSE_ICON, "icon"),
    Input(ID_AUDIO_PLAY_PAUSE_BTN, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_LEFT, "n_clicks"),
    Input(ID_SLIDESHOW_BTN_RIGHT, "n_clicks"),
    Input(ID_AUDIO_STOP_BTN, "n_clicks"),
    State(ID_AUDIO_PLAY_PAUSE_ICON, "icon"),
    prevent_initial_call=True
)
def pause_play(_start, _left, _right, _stop, icon):
    if ctx.triggered_id == ID_AUDIO_PLAY_PAUSE_BTN and "play" in icon:
            return pause_icon
    return play_icon
