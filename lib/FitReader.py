import fitparse


def read_fit(fname):
    fitfile = fitparse.FitFile(fname)

    ds = []
    delta_hs = []
    ps = []
    ts = []

    records = fitfile.get_messages("record")

    last_alt = None
    last_timestamp = None
    total_distance = None

    for record in records:
        alt = record.get_value("altitude")
        dist = record.get_value("distance")
        power = record.get_value("power")
        stamp = record.get_value("timestamp")

        if alt is not None and dist is not None and power is not None and stamp is not None:
            if last_alt is not None:
                ds.append(dist - total_distance)
                delta_hs.append(alt - last_alt)
                ps.append(power)
                ts.append((stamp - last_timestamp).total_seconds())

            total_distance = dist

            last_alt = alt
            last_timestamp = stamp

    return ds, delta_hs, ps, ts
