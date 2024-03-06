from configuration import PRIMARY_COLOR, SECONDARY_COLOR

DATA_SOURCES_WITHOUT_CHART_SUPPORT = ["Wild Cam", "Access Point"]
DATE_FORMAT = "%Y-%m-%d"
TIMEZONE = "Europe/Zurich"

SETTINGS_DRAWER_WIDTH = 400
CHART_DRAWER_HEIGHT = 500
ALERT_DURATION = 4000


app_theme = {
    "colorScheme": "light",
    "colors": {
        PRIMARY_COLOR:
            [
                "#E8F5E9",
                "#C8E6C9",
                "#A5D6A7",
                "#81C784",
                "#66BB6A",
                "#4CAF50",
                "#43A047",
                "#388E3C",
                "#2E7D32",
                "#1B5E20",
            ],
        SECONDARY_COLOR:
            [
                "#FCE4EC",
                "#F8BBD0",
                "#F48FB1",
                "#F06292",
                "#EC407A",
                "#E91E63",
                "#D81B60",
                "#C2185B",
                "#AD1457",
                "#880E4F",
            ],
    },
    "primaryColor": PRIMARY_COLOR,
    "shadows": {
        # other shadows (xs, sm, lg) will be merged from default theme
        "md": "1px 1px 3px rgba(0,0,0,.25)",
        "xl": "5px 5px 3px rgba(0,0,0,.25)",
    },
    "headings": {
        "fontFamily": "Roboto, sans-serif",
        "sizes": {
            "h1": {"fontSize": 20},
        },
    },
}

CONFIRM_UNSAVED_CHANGES_MESSAGE = "You have unsaved changes. Do you want to discard them?"
CONFIRM_DELETE_MESSAGE          = "Are you sure you want to permanently remove this item?"

supported_mime_types = [
    "image/png", 
    "image/jpeg",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
    "audio/mpeg"
]

thumbnail_size = (64, 64)
