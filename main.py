import datetime
import math
import gpxpy
import geopy.distance

rho = 1.2041
CdA = 0.25
Crr = 0.002845
m = 72
g = 9.81

gpx_file = open('test.gpx', 'r')
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
        Ps.append(260)

    last_pt = point

vs = []
ts = []

last_velocity = 5
for i in range(len(ds)):
    while True:
        arg = -2 * g * delta_hs[i] + last_velocity ** 2 - 1 / m * rho * last_velocity ** 2 * CdA * ds[i] - 2 * g * Crr + \
              Ps[i] * 2 * ds[i] / (
                      m * last_velocity)
        if arg >= 0:
            break
        else:
            Ps[i] += 10

    v = math.sqrt(arg)
    t = ds[i] / last_velocity

    vs.append(v)
    ts.append(t)
    last_velocity = v

total_time = 0
total_distance = 0
work = 0
for d, delta_h, P, t, v in zip(ds, delta_hs, Ps, ts, vs):
    print(
        f"Segment length: {d}m, Altitude Diff {delta_h}m ({delta_h / d * 100}%), Power {P}W, Time: {t}s, Speed: {v * 3.6}km/h")
    total_time += t
    total_distance += d
    work += P * t

print(
    f"Total time: {datetime.timedelta(seconds=total_time)}, "
    f"Total distance: {total_distance / 1000}km, "
    f"Avg. Speed: {total_distance / total_time * 3.6}km/h, "
    f"Work: {work/1000}kJ ({work/total_time}W Avg)")
