import fitparse
import geopy.distance


def read_fit(fname):
    fitfile = fitparse.FitFile(fname)

    ds = []
    delta_hs = []
    ps = []

    records = fitfile.get_messages("record")

    last_alt = None
    initial_timestamp = None
    last_timestamp = None
    total_distance = 0

    for record in records:
        alt = record.get_value("altitude")

        if last_alt is not None:
            ds.append(record.get_value("distance") - total_distance)
            total_distance += ds[-1]
            delta_hs.append(alt - last_alt)
            ps.append(record.get_value("power"))
            last_timestamp = record.get_value("timestamp")
        else:
            initial_timestamp = record.get_value("timestamp")

        last_alt = alt

    time = (last_timestamp - initial_timestamp).total_seconds()
    return ds, delta_hs, ps, time
