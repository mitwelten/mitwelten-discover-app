import plotly.graph_objects as go


def create_themed_figure(light_mode):
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white" if light_mode else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return figure


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

