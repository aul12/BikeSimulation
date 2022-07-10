import json


def read_params(fname):
    root = json.load(open(fname, "r"))
    fields = ["CdA", "Crr", "m", "g"]
    ret = dict()
    for field in fields:
        ret[field] = root[field]

    # https://en.wikipedia.org/wiki/Density_of_air
    temp = root["temperature"] + 273.15
    press = root["pressure"] * 100
    r_specific = 8.31446261815324 / 0.0289652
    ret["rho"] = press / (r_specific * temp)

    return ret
