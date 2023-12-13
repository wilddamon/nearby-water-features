import osmnx
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
    'emergency': 'lifeguard'
}

botanic_gardens_centrepoint = (-33.8645245,151.2170737)
river_centrepoint = (-33.9184427,151.137245)
ian_thorpe_centrepoint = (-33.8775687,151.1981906)
no_water_centrepoint = (-33.9464381,151.217986)

geodataframe = osmnx.features.features_from_point(
    botanic_gardens_centrepoint,
    water_tags,
    dist=dist
)

geodataframe = pandas.concat([
    geodataframe,
    osmnx.features.features_from_point(
        river_centrepoint,
        water_tags,
        dist=dist
        )
])

geodataframe = pandas.concat([
    geodataframe,
    osmnx.features.features_from_point(
        ian_thorpe_centrepoint,
        water_tags,
        dist=dist
        )
])


try:
    nowater = osmnx.features.features_from_point(
        no_water_centrepoint,
        water_tags,
        dist=dist
        )
    geodataframe=pandas.concat([geodataframe, nowater])
except osmnx._errors.InsufficientResponseError:
    pass
    

#bounds = [
#        [ian_thorpe_centrepoint[0]+0.005, ian_thorpe_centrepoint[1]+0.005],
#        [ian_thorpe_centrepoint[0]-0.005, ian_thorpe_centrepoint[1]-0.005]]
m = geodataframe.explore(color="red", tooltip=True, marker_kwds=mk)

folium.Marker(botanic_gardens_centrepoint, tooltip="pond/stream").add_to(m)
folium.Marker(river_centrepoint, tooltip="river").add_to(m)
folium.Marker(ian_thorpe_centrepoint, tooltip="public pool").add_to(m)
folium.Marker(no_water_centrepoint, tooltip="no water found").add_to(m)

#m.fit_bounds(bounds)
m.save("map.html")
#m.show_in_browser()
webbrowser.open('file://' + os.path.realpath('map.html'))

print('end')
