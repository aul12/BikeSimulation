import argparse
import datetime
import sys

from lib import GpxReader, FitReader, Simulation, ParamReader


def main():
    parser = argparse.ArgumentParser("Estimate the time required for a course for a fixed power")
    parser.add_argument("file", metavar="F", type=str,
                        help="The gpx file of the course")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--power", dest="power", type=float, help="Power (in Watts) for the course",
                        default=300)
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    if args.file.endswith(".gpx"):
        ds, delta_hs = GpxReader.read_gpx(args.file)
    elif args.file.endswith(".fit"):
        ds, delta_hs, _, _ = FitReader.read_fit(args.file)
    else:
        print("Unknown file format!")
        sys.exit(1)

    sim = Simulation.Simulation(ds, delta_hs)
    sim.Ps = [args.power] * len(ds)
    sim.forward(sim.Ps, params)

    print(
        f"Total time:\t\t{datetime.timedelta(seconds=sim.get_total_time())}\n"
        f"Total distance:\t{sim.get_total_distance() / 1000:.3f}km\n"
        f"Avg. Speed:\t\t{sim.get_average_speed() * 3.6:.1f}km/h\n"
        f"Work:\t\t\t{sim.get_total_work() / 1000:.0f}kJ ({sim.get_average_power():.0f}W Avg)\n"
        f"Vertical:\t\t+{sim.get_vertical_meters()[0]:.0f}m, -{sim.get_vertical_meters()[1]:.0f}m")


if __name__ == "__main__":
    main()
