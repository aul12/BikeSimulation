import argparse
import math

import matplotlib.pyplot as plt
import numpy
import scipy.optimize

from lib import FitReader, ParamReader


def estimate_cda(ds: list, delta_hs: list, Ps: list, ts: list, params):
    data_points = []

    m = params["m"]
    g = params["g"]
    Crr = params["Crr"]

    vs = [d / t for d, t in zip(ds, ts)]

    for t in range(1, len(ds)):
        P_climbing = m * g * delta_hs[t] / ds[t] * ts[t]
        a = (vs[t] - vs[t - 1]) / ts[t]
        P_acceleration = m * vs[t] * a
        P_roll = m * g * vs[t] * Crr

        P_drag = Ps[t] - P_climbing - P_acceleration - P_roll

        data_points.append((vs[t], P_drag))

    return data_points


def main():
    parser = argparse.ArgumentParser("Estimate the CdA from a .fit File")
    parser.add_argument("files", metavar="F", type=str, nargs="+",
                        help="The fit files, needs to include distance, power and altitude")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--resolution", dest="resolution", type=float, help="Required resolution of the CdA",
                        default=0.001)
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)


    segment_initial_vels = []
    segment_ds = []
    segment_delta_hs = []
    segment_Ps = []
    segment_ts = []
    initial_vel = 5

    for file in args.files:
        ds, delta_hs, Ps, ts = FitReader.read_fit(file)
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

    data_points = []
    for ds, delta_hs, Ps, ts, initial_vel in zip(segment_ds, segment_delta_hs, segment_Ps, segment_ts,
                                                 segment_initial_vels):
        data_points += estimate_cda(ds, delta_hs, Ps, ts, params)

    xs = [p[0] for p in data_points]
    ys = [p[1] for p in data_points]

    def parasitic_loss(v, CdA):
        rho = params["rho"]
        return .5 * rho * v ** 3 * CdA

    sol, cov = scipy.optimize.curve_fit(parasitic_loss, xs, ys, p0=[params["CdA"]])

    print(f"CdA: {sol[0]}m^2 (+-{math.sqrt(cov)}m^2)")

    poly_x = numpy.linspace(0, 16, 100)
    poly_y = parasitic_loss(poly_x, *sol)
    plt.scatter(xs, ys, label="Data Points")
    plt.plot(poly_x, poly_y, color="red", label="Fitted curve")
    plt.legend()
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Drag loss (W)")
    plt.title("Loss in drag power over the activity")
    plt.show()


if __name__ == "__main__":
    main()
