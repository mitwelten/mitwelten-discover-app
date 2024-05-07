DATA_SOURCES_WITHOUT_CHART_SUPPORT = ["Access Point", "Wild Cam"]
DATE_FORMAT = "%Y-%m-%d"
TIMEZONE = "Europe/Zurich"

SETTINGS_DRAWER_WIDTH = 320 
CHART_DRAWER_HEIGHT = 500
ALERT_DURATION = 4000

REFRESH_KEY_TIME_LEFT_S = 10 * 60

PRIMARY_COLOR = "mitwelten_green"
SECONDARY_COLOR = "mitwelten_pink"
BACKGROUND_COLOR = "#E8F7FC"

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
    "white": BACKGROUND_COLOR, # background color of light theme
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


EXCLUDED_DEPLOYMENTS = ["Access Point", "Phaeno Cam"]

CONFIRM_UNSAVED_CHANGES_MESSAGE = "You have unsaved changes. Do you want to discard them?"
CONFIRM_DELETE_MESSAGE          = "Are you sure you want to permanently remove this item?"

supported_mime_types = dict(
        image = ["image/png", "image/jpg", "image/jpeg", "image/gif", "image/webp"],
        audio = ["audio/mpeg"],
        doc   = ["application/pdf", "text/plain"],
        )


thumbnail_size = (64, 64)


PAX_DESCRIPTION = "The PAX sensor counts people by detecting nearby smartphones' signals. It's used to measure crowds or occupancy without invading privacy. The chart shows the number of detections, indicating how many people were nearby based on their phone signals."
AUDIO_DESCRIPTION = "An audio sensor is a device that picks up sounds in the environment. Bird songs are analysed and assigned to species using machine learning."
POLLINATOR_DESCRIPTION = "Pollinator sensors are cameras that take frequent pictures of selected plants. A machine learning model is used to search for insects on the plants and determine their genus."

DISCOVER_DESCRIPTION = 'The research project uses the lens of co-worlding to develop environmental media approaches that aim to support and foster biodiversity in urban areas by extending design research to natural, cultural and media sciences. In the project’s three case studies, media infrastructures were installed in three sites of human-environment entanglements: in the Merian Gardens near Basel, in a former port area of the city of Basel, and in a nature reserve in Reinach (Basel agglomeration). "Discover" is a map-based publication of the research results prepared for the public.'
