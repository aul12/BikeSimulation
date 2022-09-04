import fitparse
from .HeadingFromPoints import get_heading


def read_fit(fname):
    fitfile = fitparse.FitFile(fname)

    ds = []
    delta_hs = []
    Psis = []
    ps = []
    ts = []

    records = fitfile.get_messages("record")

    last_alt = None
    last_timestamp = None
    total_distance = None
    last_pt = None

    for record in records:
        alt = record.get_value("altitude")
        dist = record.get_value("distance")
        power = record.get_value("power")
        stamp = record.get_value("timestamp")
        # https://gis.stackexchange.com/a/384263
        lat = record.get_value("position_lat") * 180 / 2 ** 31
        lon = record.get_value("position_long") * 180 / 2 ** 31
        pt = (lat, lon)

        if alt is not None and dist is not None and power is not None and stamp is not None and pt is not None:
            if last_alt is not None and last_pt is not None:
                ds.append(dist - total_distance)
                delta_hs.append(alt - last_alt)
                Psis.append(get_heading(*last_pt, *pt))
                ps.append(power)
                ts.append((stamp - last_timestamp).total_seconds())

            total_distance = dist

            last_alt = alt
            last_timestamp = stamp
            last_pt = pt

    return ds, delta_hs, Psis, ps, ts
