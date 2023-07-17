DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5

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
