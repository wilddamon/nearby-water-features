import csv
import sys

import folium
import osmnx
import pandas

import water_tags

def array_to_floats(arr):
    result = []
    for n in arr:
        result.append(pandas.to_numeric(n))
    return result

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

def non_null_tags_from_gdf(gdf):
    items_retrieved = [None]*len(gdf)

    for tag in water_tags.TAGS:
        ind = gdf.reset_index()
        if tag in ind:
            for i in range(len(gdf)):
                item = ind[tag][i]
                if not pandas.isna(item):
                    items_retrieved[i] = item
    print(f"items: {items_retrieved}")
    return items_retrieved
    

def main():
    if len(sys.argv) != 3:
        raise Exception("Must specify a csv file and radius")
    data = readfile(sys.argv[1])

    # FIXME: For testing limit the number of points.
    #print(len(data))
    #data = data[:5]

    radius = int(sys.argv[2])

    #sydney_centrepoint = (-33.8472349,150.6023258)
    #m = folium.folium.Map(location=sydney_centrepoint)

    geodataframe = None
    water_found_points = []
    water_not_found_points = []
    tags_arr = []
    for latlng in data:
        print(f"total points checked: {len(water_not_found_points) + len(water_found_points)}")
        gdf = find_water_near_point(latlng, radius)
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

    m = geodataframe.explore(color="red", tooltip=True)

    plot_points(water_found_points, m, "red", tags_arr)
    plot_points(water_not_found_points, m, "blue")

    #m.save(save_path + "map.html")
    m.show_in_browser()



if __name__ == '__main__':
    sys.exit(main())
