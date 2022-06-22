import datetime

import gpxpy
import geopy.distance

import Simulation

params = {
    "rho": 1.2041,
    "CdA": 0.25,
    "Crr": 0.002845,
    "m": 72,
    "g": 9.81,
}

gpx_file = open('Hagebuchen.gpx', 'r')
gpx = gpxpy.parse(gpx_file)
assert len(gpx.tracks) == 1
assert len(gpx.tracks[0].segments) == 1
points = gpx.tracks[0].segments[0].points

ds = []
delta_hs = []
Ps = []

last_pt = points[0]
for point in points[1:]:
    d = geopy.distance.geodesic((last_pt.latitude, last_pt.longitude), (point.latitude, point.longitude)).m
    if d > 0:
        ds.append(d)
        delta_hs.append(point.elevation - last_pt.elevation)
        Ps.append(300)

    last_pt = point

sim = Simulation.Simulation(ds, delta_hs)
sim.forward(Ps, params)

print(
    f"Total time: {datetime.timedelta(seconds=sim.get_total_time())}, "
    f"Total distance: {sim.get_total_distance() / 1000}km, "
    f"Avg. Speed: {sim.get_average_speed() * 3.6}km/h, "
    f"Work: {sim.get_total_work() / 1000}kJ ({sim.get_average_power()}W Avg)")
