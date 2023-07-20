import dash_mantine_components as dmc


def action_button(action_button_id, children, color):
    return dmc.ActionIcon(
        children=children,
        id=action_button_id,
        n_clicks=0,
        className="action-button",
        color=color
    )
