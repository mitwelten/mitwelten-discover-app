import plotly.graph_objects as go


def create_themed_figure(light_mode):
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return figure



