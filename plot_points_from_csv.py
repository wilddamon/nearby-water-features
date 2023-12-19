import argparse
import collections
import csv
import os
import pprint
import sys
import webbrowser

import folium
import osmnx
import pandas

import water_tags


def plot_points(data, m, color="", tags=None):
    for i in range(len(data)):
        latlng = data[i]
        popup = ""
        if tags is not None:
            popup = f"{tags[i]}"
        folium.Marker(latlng, icon=folium.Icon(color=color), popup=popup).add_to(m)


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
    gdfs = collections.defaultdict(list)
    for i in range(len(data)):
        if i > 0 and i % 10 == 0:
            print(f"Checked {i} points")
        latlng = data[i]
        gdfs[latlng].append(find_water_near_point(latlng, radius))
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
        retrieve_value_from_gdf_row(row, "name", result)
        retrieve_value_from_gdf_row(row, "access", result)
        retrieve_value_from_gdf_row(row, "ownership", result)
        retrieve_value_from_gdf_row(row, "depth", result)
        retrieve_value_from_gdf_row(row, "lifeguard", result)

        items_retrieved.append(result)
    return items_retrieved


def accumulate_stats(
    tags_arr, names_counter, place_types_counter, num_places_found_counter
):
    for tags_dict in tags_arr:
        for key in tags_dict:
            if key == "name":
                names_counter[tags_dict["name"]] += 1
                # Only record names in the names counter
                continue
            counter_key = key
            # Separate private and public items.
            if key == "access" or key == "ownership":
                # Don't record these as they are appended below.
                continue
            key_name = f"{key}:{tags_dict[key]}"
            if "access" in tags_dict:
                key_name = f'{key_name}_{tags_dict["access"]}'
            elif "ownership" in tags_dict:
                key_name = f'{key_name}_{tags_dict["ownership"]}'
            place_types_counter[key_name] += 1

        num_places_found_counter[len(tags_dict)] += 1


def run(data, radius, save_path=None, open_in_browser=False):
    print(f"Finding water near {len(data)} points")
    gdfs = find_water_near_points(data, radius)

    geodataframe = None
    water_found_points = []
    water_not_found_points = []
    tags_arr = []
    place_types_counter = collections.Counter()
    place_names_counter = collections.Counter()
    num_places_found_counter = collections.Counter()
    for latlng in gdfs:
        gdf_arr = gdfs[latlng]
        for gdf in gdf_arr:
            if gdf is None:
                water_not_found_points.append(latlng)
                num_places_found_counter[0] += 1
                continue

            tags = non_null_tags_from_gdf(gdf)
            if geodataframe is None:
                geodataframe = gdf
            else:
                geodataframe = pandas.concat([geodataframe, gdf])
            water_found_points.append(latlng)
            tags_arr.append(tags)

            accumulate_stats(
                tags, place_names_counter, place_types_counter, num_places_found_counter
            )

    print(f"Found water near {len(water_found_points)} of {len(data)}")
    pprint.pprint(place_types_counter)
    pprint.pprint(place_names_counter)
    pprint.pprint(num_places_found_counter)

    if open_in_browser:
        m = geodataframe.explore(color="red", tooltip=True)

        plot_points(water_found_points, m, "red", tags_arr)
        plot_points(water_not_found_points, m, "blue")

    if save_path:
        save_path = os.path.realpath(save_path)
        print(f"saving to {save_path}")
        m.save(save_path)
        if open_in_browser:
            webbrowser.open("file://" + save_path)
    elif open_in_browser:
        m.show_in_browser()


def main():
    parser = argparse.ArgumentParser(
        prog="plot_points_from_csv",
        description="gets water features from a specified radius around points,"
        + "and plots them on a map.",
    )
    parser.add_argument("filename")
    parser.add_argument("radius", type=int)
    parser.add_argument("--limit_points", type=int, required=False)
    parser.add_argument("--save_path", required=False)
    parser.add_argument(
        "--open", required=False, action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--latitude_colname", required=False)
    parser.add_argument("--longitude_colname", required=False)
    parser.add_argument(
        "--has_header",
        required=False,
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    args = parser.parse_args()
    if (args.latitude_colname and args.longitude_colname is None) or (
        args.longitude_colname and args.latitude_colname is None
    ):
        parser.error(
            "If either latitude_colname or longitude_colname is specified,"
            + " the other must be too."
        )

    header = "infer" if args.has_header else None
    if args.latitude_colname:
        pandas_data = pandas.read_csv(
            args.filename,
            usecols=[args.latitude_colname, args.longitude_colname],
            header=header,
        )
    else:
        pandas_data = pandas.read_csv(args.filename, header=header)

    data = []
    end_index = len(pandas_data)
    if args.limit_points and args.limit_points < len(pandas_data):
        end_index = args.limit_points

    lat_key = args.latitude_colname if args.latitude_colname else 0
    lng_key = args.longitude_colname if args.longitude_colname else 1
    for i in range(end_index):
        # Exclude if missing latlng
        if pandas.isna(pandas_data[lat_key][i]) or pandas.isna(pandas_data[lng_key][i]):
            continue
        data.append((pandas_data[lat_key][i], pandas_data[lng_key][i]))

    run(data, args.radius, save_path=args.save_path, open_in_browser=args.open)


if __name__ == "__main__":
    sys.exit(main())
