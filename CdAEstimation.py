import datetime
import argparse

from lib import FitReader, Simulation, ParamReader


def main():
    parser = argparse.ArgumentParser("Estimate the CdA from a .fit File")
    parser.add_argument("file", metavar="F", type=str,
                        help="The fit file, needs to include distance, power and altitude")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--resolution", dest="resolution", type=float, help="Required resolution of the CdA",
                        default=0.001)
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    ds, delta_hs, Ps, real_total_time = FitReader.read_fit(args.file)

    sim = Simulation.Simulation(ds, delta_hs)

    lower_bound = 0
    upper_bound = 1

    while abs(upper_bound - lower_bound) > args.resolution:
        mid = (upper_bound + lower_bound) / 2
        params["CdA"] = mid

        sim.forward(Ps, params)

        if sim.get_total_time() > real_total_time:
            # reduce cda
            upper_bound = mid
        else:
            lower_bound = mid

        print(f"\rCdA:\t\t\t\t\t{mid}m^2", end="")

    print(
        f"\nSimulated Total time:\t{datetime.timedelta(seconds=sim.get_total_time())}s\n"
        f"Real Total time:\t\t{datetime.timedelta(seconds=real_total_time)}s\n"
        f"Total distance:\t\t\t{sim.get_total_distance() / 1000}km\n"
        f"Avg. Speed:\t\t\t\t{sim.get_average_speed() * 3.6}km/h\n")


if __name__ == "__main__":
    main()
