
TAGS = {
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
        'paddling_pool',
        'marina',
        'hot_tub',
        'bathing_place',
    ],
    'man_made': [
        'storage_tank',
        'tailings_pond',
        'water_well',
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
    'swimming_pool': True,
    'animal': ['swimming']

    # consider
    # 'playground': ['splash_pad'],
}

# Equivalent tags:
# leisure:swimming_pool and leisure:sports_centre+sport:swimming
