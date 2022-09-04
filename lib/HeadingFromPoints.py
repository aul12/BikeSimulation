import math


# https://stackoverflow.com/a/17662363
def get_heading(last_lat: float, last_long: float, lat: float, long: float) -> float:
    d_lon = long - last_long
    y = math.sin(d_lon) * math.cos(lat)
    x = math.cos(last_lat) * math.sin(lat) - math.sin(last_lat) * math.cos(lat) * math.cos(d_lon)
    return -math.atan2(y, x)
