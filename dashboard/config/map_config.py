import itertools

DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5
DEFAULT_MAP_INDEX = 1
DEFAULT_MARKER_COLORS = [
    "#FF5733",  # (Pastell Orange)
    "#9B59B6",  # (Lavendelviolett)
    "#F1C40F",  # (Sonnenblumengelb)
    "#3498DB",  # (Hellblau)
    "#E67E22",  # (Terra Cotta)
    "#2ECC71",  # (Smaragdgrün)
    "#E74C3C",  # (Tomatenrot)
    "#1ABC9C",  # (Türkis)
    "#F39C12",  # (Goldgelb)
    "#FF00FF",  # (Magenta)
]

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
            source,
            source_attribution,
            style="white-bg",
            layers=None
    ):
        if layers is None:
            layers = {}

        self.id = next(self.iter_id)
        self.title = title
        self.image = image
        self.source = source
        self.source_attribution = source_attribution
        self.style = style
        self.layers = layers


map_configs = [
    # MapConfiguration(
    #     title="Carto",
    #     image="./assets/minimap/carto.png",
    #     style="carto-positron"
    # ),
    # MapConfiguration(
    #     title="Carto Dark",
    #     image="./assets/minimap/carto-dark.png",
    #     style="carto-darkmatter",
    # ),
    # MapConfiguration(
    #     title="Stamen Toner",
    #     image="./assets/minimap/stamen-toner.png",
    #     style="stamen-toner",
    # ),
    # MapConfiguration(
    #     title="Stamen Terrain",
    #     image="./assets/minimap/stamen-terrain.png",
    #     style="stamen-terrain",
    # ),
    MapConfiguration(
        title="Open Street Map",
        image="./assets/minimap/open-street.png",
        source="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        source_attribution='© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
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
        source="https://wmts10.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
        layers=DEFAULT_MAP_LAYER,
    ),
    MapConfiguration(
        title="Swiss Topo Grey",
        image="./assets/minimap/swiss-topo-grey.png",
        source="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
        layers=PIXEL_GREY_MAP_LAYER,
    ),
    MapConfiguration(
        title="Swiss Topo Color",
        image="./assets/minimap/swiss-topo-color.png",
        source="https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg",
        source_attribution='<a href="https://www.swisstopo.admin.ch/de/home.html" target="_blank">SwissTopo</a>',
        layers=PIXEL_COLOR_MAP_LAYER,
    ),
]
