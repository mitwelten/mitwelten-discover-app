import itertools

DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5
DEFAULT_MAP_INDEX = 1

DEFAULT_MAP_LAYER = {
    "below": "traces",
    "sourcetype": "raster",
    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    "source": [
        "https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
    ],
}

PIXEL_COLOR_MAP_LAYER = {
    "below": "traces",
    "sourcetype": "raster",
    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    "source": [
        "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg"
    ],
}

PIXEL_GREY_MAP_LAYER = {
    "below": "traces",
    "sourcetype": "raster",
    "sourceattribution": '<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
    "source": [
        "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg"
    ],
}


class MapConfiguration:
    iter_id = itertools.count()

    def __init__(
            self,
            title,
            image,
            style="white-bg",
            layers=None
    ):
        if layers is None:
            layers = {}

        self.id = next(self.iter_id)
        self.title = title
        self.image = image
        self.style = style
        self.layers = layers


map_configs = [
    MapConfiguration(
        title="Carto",
        image="./assets/minimap/carto.png",
        style="carto-positron"
    ),
    MapConfiguration(
        title="Carto Dark",
        image="./assets/minimap/carto-dark.png",
        style="carto-darkmatter",
    ),
    MapConfiguration(
        title="Stamen Toner",
        image="./assets/minimap/stamen-toner.png",
        style="stamen-toner",
    ),
    MapConfiguration(
        title="Stamen Terrain",
        image="./assets/minimap/stamen-terrain.png",
        style="stamen-terrain",
    ),
    MapConfiguration(
        title="Open Street Map",
        image="./assets/minimap/open-street.png",
        style="open-street-map",
    ),
    # MapConfiguration(
    #     title="Stamen Watercolor",
    #     image="./assets/minimap-carto-dark.png",
    #     style="stamen-watercolor",
    # ),
    MapConfiguration(
        title="Swiss Topo Picture",
        image="./assets/minimap/swiss-topo-picture.png",
        layers=DEFAULT_MAP_LAYER,
    ),
    MapConfiguration(
        title="Swiss Topo Grey",
        image="./assets/minimap/swiss-topo-grey.png",
        layers=PIXEL_GREY_MAP_LAYER,
    ),
    MapConfiguration(
        title="Swiss Topo Color",
        image="./assets/minimap/swiss-topo-color.png",
        layers=PIXEL_COLOR_MAP_LAYER,
    ),
]
