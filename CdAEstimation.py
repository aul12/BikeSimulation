import datetime
import argparse

from lib import FitReader, Simulation, ParamReader


def estimate_cda(ds: list, delta_hs: list, Ps: list, ts: list, initial_vel: float, params, resolution: float):
    real_total_time = 0
    for t in ts:
        real_total_time += t

    sim = Simulation.Simulation(ds, delta_hs)

    lower_bound = 0
    upper_bound = 1

    mid = None
    while abs(upper_bound - lower_bound) > resolution:
        mid = (upper_bound + lower_bound) / 2
        params["CdA"] = mid

        sim.forward(Ps, params, initial_velocity=initial_vel)

        sim_total_time = 0
        for t in sim.ts:
            sim_total_time += t

        if sim_total_time > real_total_time:
            # reduce cda
            upper_bound = mid
        else:
            lower_bound = mid

    return mid


def main():
    parser = argparse.ArgumentParser("Estimate the CdA from a .fit File")
    parser.add_argument("file", metavar="F", type=str,
                        help="The fit file, needs to include distance, power and altitude")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--resolution", dest="resolution", type=float, help="Required resolution of the CdA",
                        default=0.001)
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    ds, delta_hs, Ps, ts = FitReader.read_fit(args.file)

    segment_initial_vels = []
    segment_ds = []
    segment_delta_hs = []
    segment_Ps = []
    segment_ts = []
    initial_vel = 5

    last_was_zero = True
    for d, delta_h, P, t in zip(ds, delta_hs, Ps, ts):
        if P > 50:
            if last_was_zero:
                segment_ds.append([d])
                segment_delta_hs.append([delta_h])
                segment_Ps.append([P])
                segment_ts.append([t])
                segment_initial_vels.append(initial_vel)
            else:
                segment_ds[-1].append(d)
                segment_delta_hs[-1].append(delta_h)
                segment_Ps[-1].append(P)
                segment_ts[-1].append(t)
            last_was_zero = False
        else:
            initial_vel = d / t
            last_was_zero = True

    cdas = []
    for ds, delta_hs, Ps, ts, initial_vel in zip(segment_ds, segment_delta_hs, segment_Ps, segment_ts,
                                                 segment_initial_vels):
        cdas.append(estimate_cda(ds, delta_hs, Ps, ts, initial_vel, params, args.resolution))


    weighted_cda_sum = 0
    total_sum = 0
    for i in range(len(cdas)):
        weighted_cda_sum += cdas[i] * len(segment_Ps[i])
        total_sum += len(segment_Ps[i])

    cda = weighted_cda_sum / total_sum
    print(f"{cda}m^2")


if __name__ == "__main__":
    main()
