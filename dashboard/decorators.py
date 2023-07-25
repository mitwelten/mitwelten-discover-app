import dash_mantine_components as dmc
from dash import html


def spaced_section(content_func):

    def inner(*args, **kwargs):
        elems = content_func(*args, **kwargs)
        pre = dmc.Space(h=10)
        post = dmc.Space(h=30)
        return html.Div([pre, elems, post])

    return inner
