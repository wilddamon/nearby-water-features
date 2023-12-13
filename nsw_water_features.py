import osmnx
import geopandas
import webbrowser
import os
import folium

water_tags = {
    "natural": [
        "water",  # inland water bodies
        "bay",
        "beach",
        "blowhole",
        "coastline",
        "shoal",
        "spring",
        "wetland",
    ],
    "water": True,
    "waterway": [
        "river",
        "stream",
        "tidal_channel",
        "canal",
        "drain",
        "ditch",
        "dam",
        "weir",
        "waterfall",
    ],
    "leisure": [
        "swimming_pool",
        "swimming_area",
        "water_park",
        "marina",
    ],
    "man_made": [
        "storage_tank",
        "tailings_pond",
        "water_well",
    ],
    "place": [
        "sea",
        "ocean",
    ],
    "sport": [
        "swimming",  # marks indoor facilities used for these sports
        "scuba_diving",
    ],
    "amenity": [
        "fountain",
        "dive_centre",
        "public_bath",
        "spa",
    ],
}

water_features_nsw = osmnx.features.features_from_place(
    "New South Wales, Australia", water_tags
)

m = water_features_nsw.explore(color="red", zoom_start=6)
m.show_in_browser()
