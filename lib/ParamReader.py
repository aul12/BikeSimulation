import json


def read_params(fname):
    root = json.load(open(fname, "r"))
    fields = ["rho", "CdA", "Crr", "m", "g"]
    ret = dict()
    for field in fields:
        ret[field] = root[field]
    return ret
