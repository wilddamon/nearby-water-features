import argparse
import csv
import os
import pprint
import sys
import webbrowser

import folium
import osmnx
import pandas

import water_tags

def array_to_floats(arr):
    result = []
    for n in arr:
        result.append(pandas.to_numeric(n))
    return tuple(result)

def readfile(path):
    data = []
    with open(path, newline='', mode='r', encoding='utf-8-sig') as csvfile:
        rdr = csv.reader(csvfile)
        for row in rdr:
            data.append(array_to_floats(row))
    return data

def plot_points(data, m, color="", tags=None):
    for i in range(len(data)):
        latlng = data[i]
        popup = ""
        if tags is not None:
            popup = f"{tags[i]}"
        folium.Marker(
                latlng,
                icon=folium.Icon(color=color),
                popup=popup
                ).add_to(m)
        

def find_water_near_point(latlng, radius):
    try:
        return osmnx.features.features_from_point(
            latlng,
            water_tags.TAGS,
            dist=radius,
        )
    except osmnx.features.InsufficientResponseError:
        return None

def find_water_near_points(data, radius):
    gdfs = {}
    for i in range(len(data)):
        if i > 0 and i % 10 == 0:
            print(f'Checked {i} points')
        latlng = data[i]
        gdfs[latlng] = find_water_near_point(latlng, radius)
    return gdfs

def retrieve_value_from_gdf_row(row, tag, result_dict):
    if tag in row and not pandas.isna(row[tag]):
        result_dict[tag] = row[tag]

def non_null_tags_from_gdf(gdf):
    items_retrieved = []

    for iterrow in gdf.iterrows():
        row = iterrow[1]
        result = {}
        for tag in water_tags.TAGS:
            retrieve_value_from_gdf_row(row, tag, result)
        retrieve_value_from_gdf_row(row, 'name', result)
        retrieve_value_from_gdf_row(row, 'access', result)
        retrieve_value_from_gdf_row(row, 'ownership', result)
        retrieve_value_from_gdf_row(row, 'depth', result)
        retrieve_value_from_gdf_row(row, 'lifeguard', result)

        items_retrieved.append(result)
    return items_retrieved

def accumulate_in_dict(d, key):
    if not key in d:
        d[key] = 0
    d[key] += 1

def accumulate_in_subdict(d, key, subkey):
    if not key in d:
        d[key] = {}
    if not subkey in d[key]:
        d[key][subkey] = 0
    d[key][subkey] += 1

def accumulate_stats(tags_arr, results_dict):
    for tags_dict in tags_arr:
        for key in tags_dict.keys():
            if (key == 'name'):
                accumulate_in_subdict(results_dict, 'names', tags_dict[key])
                continue
            key_name = f"{key}:{tags_dict[key]}"
            if key != 'access' and 'access' in tags_dict:
                key_name = f'{key_name}_{tags_dict["access"]}'
            if key != 'ownership' and 'ownership' in tags_dict:
                key_name = f'{key_name}_{tags_dict["ownership"]}'
            accumulate_in_dict(results_dict, key_name)

        num_keys = len(tags_dict.keys())
        accumulate_in_subdict(results_dict, 'num_items_found', num_keys)

def main():
    if len(sys.argv) < 3:
        raise Exception("Must specify a csv file and radius")

    parser = argparse.ArgumentParser(
        prog='plot_points_from_csv',
        description='gets water features from a specified radius around points,' +
            'and plots them on a map.',
        )
    parser.add_argument('filename')
    parser.add_argument('radius', type=int)
    parser.add_argument('--limit_points', type=int, required=False)
    parser.add_argument('--save_path', required=False)
    parser.add_argument(
        '--open',
        required=False,
        action=argparse.BooleanOptionalAction,
        default=True)
    args = parser.parse_args()

    data = readfile(args.filename)

    if args.limit_points and len(data) > args.limit_points:
        data = data[:args.limit_points]

    print(f"Finding water near {len(data)} points")
    gdfs = find_water_near_points(data, args.radius)
    print(f"Found water near {len(gdfs.keys())} of {len(data)}")

    geodataframe = None
    water_found_points = []
    water_not_found_points = []
    tags_arr = []
    stats = {}
    for latlng in gdfs:
        gdf = gdfs[latlng]
        if gdf is None:
            water_not_found_points.append(latlng)
            continue

        tags = non_null_tags_from_gdf(gdf)
        if geodataframe is None:
            geodataframe = gdf
        else:
            geodataframe = pandas.concat([geodataframe, gdf])
        water_found_points.append(latlng)
        tags_arr.append(tags)
        accumulate_stats(tags, stats)

    pprint.pprint(stats)

    if args.open:
        m = geodataframe.explore(color="red", tooltip=True)

        plot_points(water_found_points, m, "red", tags_arr)
        plot_points(water_not_found_points, m, "blue")

    if args.save_path:
        save_path = os.path.realpath(args.save_path)
        print(f"saving to {save_path}")
        m.save(save_path)
        if args.open:
            webbrowser.open('file://' + save_path)
    elif args.open:
        m.show_in_browser()



if __name__ == '__main__':
    sys.exit(main())
