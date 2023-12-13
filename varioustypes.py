import osmnx
import random
import geopandas
import webbrowser
import os
import folium
import pandas

tiles = "cartodbdarkmatter"
mk = {"radius": 6}
dist = 100 # metres
tooltip = [
    "name", 
    "natural",
    "water",
    "leisure",
    "man_made",
    #"place",
    "sport",
    "amenity",
    "note"
]

water_tags = {
    'natural': [
        'water', # inland water bodies
        'bay',
        'beach',
        'blowhole',
        'coastline',
        'shoal',
        'spring',
        'wetland',
    ],   
    'water': True,
    'waterway': [
        'river',
        'stream',
        'tidal_channel',
        'canal',
        'drain',
        'ditch',
        'dam',
        'weir',
        'waterfall',
    ],
    'leisure': [
        'swimming_pool',
        'swimming_area',
        'water_park',
        'marina',
    ],
    'man_made': [
        'storage_tank',
        'tailings_pond',
        'water_well',
    ],
    'place': [
        'sea',
        'ocean',
    ],
    'sport': [
        'swimming', # marks indoor facilities used for these sports
        'scuba_diving',
    ],
    'amenity': [
        'fountain',
        'dive_centre',
        'public_bath',
        'spa',
    ],
}

lifeguard_tags = {
    'emergency': 'lifeguard',
}

centrepoints = [
    (-33.8645245,151.2170737),
    (-33.9184427,151.137245),
    (-33.8775687,151.1981906),
    (-33.9464381,151.217986),
    (-33.876851,151.203764)
]

# Generate random points between
lat_min = -33.971504
lat_max = -33.836438
long_min = 151.0218361
long_max = 151.2803581
random_lat_range = (lat_max - lat_min)
random_lat_centre = (lat_min + lat_max) / 2
random_long_range = long_max - long_min
random_long_centre = (long_min + long_max) / 2
generated_centrepoints = []
for i in range(20):
    generated_centrepoints.append(
        (
            (random.random() - 0.5)*random_lat_range + random_lat_centre,
            (random.random() - 0.5)*random_long_range + random_long_centre
        )
    )

print(generated_centrepoints)

geodataframe = osmnx.features.features_from_point(
    centrepoints[0],
    water_tags,
    dist=dist
)

all_points = centrepoints + generated_centrepoints
for point in all_points[1:]:
    try:
        frame = osmnx.features.features_from_point(
            point,
            water_tags,
            dist=dist,
            )
        geodataframe = pandas.concat([geodataframe, frame])
    except osmnx.features.InsufficientResponseError:
        pass

m = geodataframe.explore(color="red", tooltip=True, marker_kwds=mk)

for point in all_points:
    folium.Marker(point).add_to(m)

m.save("map.html")
webbrowser.open('file://' + os.path.realpath('map.html'))

print('end')
