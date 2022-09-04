import math

import gpxpy
import geopy.distance
from .HeadingFromPoints import get_heading


def read_gpx(path):
    gpx_file = open(path, 'r')
    gpx = gpxpy.parse(gpx_file)
    assert len(gpx.tracks) == 1
    assert len(gpx.tracks[0].segments) == 1
    points = gpx.tracks[0].segments[0].points

    ds = []
    delta_hs = []
    Psis = []

    last_pt = points[0]
    for point in points[1:]:
        d = geopy.distance.geodesic((last_pt.latitude, last_pt.longitude), (point.latitude, point.longitude)).m

        Psi = get_heading(last_pt.latitude / 180 * math.pi, last_pt.longitude / 180 * math.pi,
                          point.latitude / 180 * math.pi, point.longitude / 180 * math.pi)

        if d > 0:
            ds.append(d)
            Psis.append(Psi)
            delta_hs.append(point.elevation - last_pt.elevation)

        last_pt = point

    return ds, delta_hs, Psis
