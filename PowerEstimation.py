import argparse
import datetime

from lib import GpxReader, Simulation, ParamReader


def main():
    parser = argparse.ArgumentParser("Estimate the time required for a course for a fixed power")
    parser.add_argument("file", metavar="F", type=str,
                        help="The gpx file of the course")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--resolution", dest="resolution", type=float, help="Required resolution for the power",
                        default=0.001)
    parser.add_argument("--time", dest="time", type=str, help="Time for the segment")
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    ds, delta_hs = GpxReader.read_gpx(args.file)

    sim = Simulation.Simulation(ds, delta_hs)

    lower_bound = 0
    upper_bound = 2000

    real_total_time = (datetime.datetime.strptime(args.time, "%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()

    while abs(upper_bound - lower_bound) > args.resolution:
        mid = (upper_bound + lower_bound) / 2

        sim.forward([mid] * len(ds), params)

        if sim.get_total_time() > real_total_time:
            lower_bound = mid
        else:
            upper_bound = mid

    print(
        f"\nSimulated Total time:\t{datetime.timedelta(seconds=sim.get_total_time())}\n"
        f"Real Total time:\t\t{datetime.timedelta(seconds=real_total_time)}\n"
        f"Total distance:\t\t\t{sim.get_total_distance() / 1000:.3f}km\n"
        f"Avg. Speed:\t\t\t\t{sim.get_average_speed() * 3.6:.1f}km/h\n"
        f"Work:\t\t\t\t\t{sim.get_total_work() / 1000:.0f}kJ ({sim.get_average_power():.0f}W Avg)\n"
        f"Vertical:\t\t\t\t+{sim.get_vertical_meters()[0]:.0f}m, -{sim.get_vertical_meters()[1]:.0f}m")


if __name__ == "__main__":
    main()
