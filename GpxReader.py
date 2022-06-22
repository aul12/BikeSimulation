import gpxpy
import geopy.distance


def read_gpx(path):
    gpx_file = open(path, 'r')
    gpx = gpxpy.parse(gpx_file)
    assert len(gpx.tracks) == 1
    assert len(gpx.tracks[0].segments) == 1
    points = gpx.tracks[0].segments[0].points

    ds = []
    delta_hs = []

    last_pt = points[0]
    for point in points[1:]:
        d = geopy.distance.geodesic((last_pt.latitude, last_pt.longitude), (point.latitude, point.longitude)).m
        if d > 0:
            ds.append(d)
            delta_hs.append(point.elevation - last_pt.elevation)

        last_pt = point

    return ds, delta_hs
