import random

import plot_points_from_csv

# Generate random points between
lat_min = -33.971504
lat_max = -33.836438
long_min = 151.0218361
long_max = 151.2803581
random_lat_range = lat_max - lat_min
random_lat_centre = (lat_min + lat_max) / 2
random_long_range = long_max - long_min
random_long_centre = (long_min + long_max) / 2
generated_centrepoints = []
for i in range(20):
    generated_centrepoints.append(
        (
            (random.random() - 0.5) * random_lat_range + random_lat_centre,
            (random.random() - 0.5) * random_long_range + random_long_centre,
        )
    )


plot_points_from_csv.run(
    generated_centrepoints, 100, 0, output_dir="../maps-html/", open_in_browser=True
)
