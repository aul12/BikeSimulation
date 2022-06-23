import fitparse


def read_fit(fname):
    fitfile = fitparse.FitFile(fname)

    ds = []
    delta_hs = []
    ps = []

    records = fitfile.get_messages("record")

    last_alt = None
    initial_timestamp = None
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
                last_timestamp = stamp
            else:
                initial_timestamp = stamp

            total_distance = dist

            last_alt = alt

    time = (last_timestamp - initial_timestamp).total_seconds()
    return ds, delta_hs, ps, time
