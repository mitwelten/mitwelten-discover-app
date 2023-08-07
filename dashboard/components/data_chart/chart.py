import plotly.graph_objects as go


def create_figure_from_timeseries(series, light_mode, x_label="time", y_label="value"):
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    print(series)
    print(x_label)
    figure.add_trace(go.Scatter(
        x=series[x_label],
        y=series[y_label],
    ))
    return figure



