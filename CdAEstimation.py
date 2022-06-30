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
    ds, delta_hs, Ps, ts = FitReader.read_fit(args.file)

    real_total_time = 0
    real_total_time_zero_power = 0
    for t in range(len(ts)):
        real_total_time += ts[t]
        if Ps[t] < 10:
            real_total_time_zero_power += ts[t]
    real_relevant_time = real_total_time - real_total_time_zero_power

    sim = Simulation.Simulation(ds, delta_hs)

    lower_bound = 0
    upper_bound = 1

    while abs(upper_bound - lower_bound) > args.resolution:
        mid = (upper_bound + lower_bound) / 2
        params["CdA"] = mid

        sim.forward(Ps, params)

        sim_total_time = 0
        sim_total_time_zero_power = 0
        for t in range(len(sim.ts)):
            sim_total_time += sim.ts[t]
            if Ps[t] < 10:
                sim_total_time_zero_power += sim.ts[t]
        sim_relevant_time = sim_total_time - sim_total_time_zero_power

        if sim_relevant_time > real_relevant_time:
            # reduce cda
            upper_bound = mid
        else:
            lower_bound = mid

        print(f"\rCdA:\t\t\t\t\t{mid}m^2", end="")

    print(
        f"\nSimulated Total time:\t{datetime.timedelta(seconds=sim.get_total_time())}\n"
        f"Real Total time:\t\t{datetime.timedelta(seconds=real_total_time)}\n"
        f"Total distance:\t\t\t{sim.get_total_distance() / 1000:.3f}km\n"
        f"Avg. Speed:\t\t\t\t{sim.get_average_speed() * 3.6:.1f}km/h\n")


if __name__ == "__main__":
    main()
