import argparse
import copy

import matplotlib.pyplot as plt
import numpy

from lib import FitReader, ParamReader, Simulation


def get_sigma_points(x: numpy.ndarray, cov: numpy.ndarray, kappa=None):
    if kappa is None:
        kappa = 3 - x.size

    sigma_pts = []
    sigma_weights = []

    sigma_pts.append(x)
    sigma_weights.append(kappa / (x.size + kappa))

    chol = numpy.linalg.cholesky(cov)
    for c in range(x.size):
        dir_vec = chol[c]
        sigma_pts.append(x + dir_vec)
        sigma_pts.append(x - dir_vec)
        weights = 1 / (2 * (x.size + kappa))
        sigma_weights.append(weights)
        sigma_weights.append(weights)

    return sigma_pts, sigma_weights


def get_mean_cov_from_sigma_pts(pts: list, weights: list):
    mean = numpy.zeros(pts[0].shape)
    for pt, weight in zip(pts, weights):
        mean += pt * weight

    cov = numpy.zeros((pts[0].size, pts[0].size))
    for pt, weight in zip(pts, weights):
        diff = pt - mean
        cov += weight * numpy.outer(diff, diff)

    return mean, cov


def simultaneous_state_paramter_estimation(ds: list, delta_hs: list, Ps: list, ts: list, params,
                                           init_cda=None, init_crr=None):
    vs = [d / t for d, t in zip(ds, ts)]

    if init_cda is None:
        init_cda = params["CdA"]

    if init_crr is None:
        init_crr = params["Crr"]

    # State: Velocity, Gradient, Power; CdA, Crr
    x0 = numpy.array([vs[0], delta_hs[0] / ds[0], Ps[0], init_cda, init_crr])

    def f(x, t):
        v = x[0]
        g = x[1]
        P = x[2]
        CdA = x[3]
        Crr = x[4]
        try:
            new_params = copy.deepcopy(params)
            new_params["CdA"] = CdA
            new_params["Crr"] = Crr
            new_vel = Simulation.Simulation.get_velocity(last_velocity=v, P=P, delta_h=ds[t] * g, d=ds[t],
                                                         params=new_params)
        except ValueError:
            new_vel = 0

        return numpy.array([
            new_vel,
            g,
            P,
            CdA,
            Crr
        ])

    def h(x):
        v = x[0]
        g = x[1]
        P = x[2]
        return numpy.array([
            v,
            g,
            P
        ])

    d_average = sum(ds) / len(ds)
    pwr_average = sum(Ps) / len(Ps)

    R = numpy.diagflat([2 * 3 / (1 ** 2), (0.2 / d_average) ** 2, (pwr_average * 0.01) ** 2])
    Q = numpy.diagflat([0.001, 0.2, 10, 0.1, 0.1])

    x = x0
    P = numpy.identity(5)

    xs = [x0]

    nies_samples = []

    for t in range(1, len(ds)):
        z = numpy.array([vs[t], delta_hs[t] / ds[t], Ps[t]])

        pred_x_pts, weights = get_sigma_points(x, P)
        pred_x_pts = [f(x, t) for x in pred_x_pts]
        pred_x, pred_cov = get_mean_cov_from_sigma_pts(pred_x_pts, weights)
        pred_cov += Q

        meas_x_pts, _ = get_sigma_points(pred_x, pred_cov)
        meas_z_pts = [h(x) for x in meas_x_pts]
        pred_z, pred_z_cov = get_mean_cov_from_sigma_pts(meas_z_pts, weights)
        pred_z_cov += R

        correlation = numpy.zeros((pred_x.size, pred_z.size))
        for weight, measXPt, measZPt in zip(weights, meas_x_pts, meas_z_pts):
            correlation += weight * numpy.outer(measXPt - pred_x, measZPt - pred_z)

        kalman_gain = correlation @ numpy.linalg.inv(pred_z_cov)

        nies_samples.append((z - pred_z).transpose() @ numpy.linalg.inv(pred_z_cov) @ (z - pred_z))

        x = pred_x + kalman_gain @ (z - pred_z)
        P = pred_cov - kalman_gain @ pred_z_cov @ kalman_gain.transpose()

        while not numpy.all(numpy.linalg.eigvals(P) > 0):
            print("Hacky hack hack")
            P += numpy.identity(P.shape[0]) * abs(numpy.linalg.det(P)) * 2

        xs.append(x)

    filtered_vs = [x[0] for x in xs]
    filtered_delta_hs = [x[1] * ds[t] for t, x in enumerate(xs)]
    filtered_Ps = [x[2] for x in xs]
    CdAs = [x[3] for x in xs]
    Crrs = [x[4] for x in xs]

    plt.plot(vs, label="Measurement")
    plt.plot(filtered_vs, label="Filtered")
    plt.title("Velocity")
    plt.legend()
    plt.show()

    plt.plot(Ps, label="Measurement")
    plt.plot(filtered_Ps, label="Filtered")
    plt.title("P")
    plt.legend()
    plt.show()

    plt.plot(delta_hs, label="Measurement")
    plt.plot(filtered_delta_hs, label="Filtered")
    plt.title("delta_h")
    plt.legend()
    plt.show()

    plt.plot(CdAs)
    plt.title("CdA")
    plt.show()

    plt.plot(Crrs)
    plt.title("Crr")
    plt.show()

    plt.hist(nies_samples)
    plt.show()

    return CdAs[-1], Crrs[-1]


def main():
    parser = argparse.ArgumentParser("Estimate the CdA from a .fit File")
    parser.add_argument("files", type=str, nargs="+",
                        help="The fit files, needs to include distance, power and altitude")
    parser.add_argument("--params", dest="params", type=str, default="params.json",
                        help="Params file, the CdA in the file is used as initial estimate")
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)

    segment_ds = []
    segment_delta_hs = []
    segment_Ps = []
    segment_ts = []

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
                else:
                    segment_ds[-1].append(d)
                    segment_delta_hs[-1].append(delta_h)
                    segment_Ps[-1].append(P)
                    segment_ts[-1].append(t)
                last_was_zero = False
            else:
                last_was_zero = True

    CdA = None
    Crr = None
    for ds, delta_hs, Ps, ts in zip(segment_ds, segment_delta_hs, segment_Ps, segment_ts):
        if len(ds) > 10:
            CdA, Crr = simultaneous_state_paramter_estimation(ds, delta_hs, Ps, ts, params, CdA, Crr)


if __name__ == "__main__":
    main()
