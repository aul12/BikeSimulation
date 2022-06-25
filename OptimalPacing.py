import argparse
import datetime
import math

import sympy

from lib import GpxReader, Simulation, ParamReader


def main():
    parser = argparse.ArgumentParser("Estimate the optimal power profile for a course")
    parser.add_argument("file", metavar="F", type=str,
                        help="The gpx file of the course")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--power", dest="power", type=float, help="Average Power (in Watts) for the course",
                        default=300)
    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    ds, delta_hs = GpxReader.read_gpx(args.file)

    sim = Simulation.Simulation(ds, delta_hs)
    sim.Ps = [args.power] * len(ds)

    sim.forward(sim.Ps, params)
    last_time = sim.get_total_time()

    # System description:
    #   v_{t+1} = f(v_t, P_t)
    # State cost = t = d/v_t, Control Cost = 0
    v_t, P_t, d_t, delta_h_t = sympy.symbols("v_t, P_t, d_t, delta_h_t")
    f = sim.get_velocity(v_t, P_t, d_t, delta_h_t, params)
    a_t_sym = f.diff(v_t)
    b_t_sym = f.diff(P_t)

    state_cost_sym = d_t / v_t
    q_t_sym = state_cost_sym.diff(v_t)

    for c in range(10):
        # Back pass
        cost = 0
        steps = [0] * len(ds)

        for t in range(len(ds) - 1, 0, -1):
            bindings = {
                v_t: sim.vs[t],
                P_t: sim.Ps[t],
                d_t: ds[t],
                delta_h_t: delta_hs[t]
            }

            a_t = float(a_t_sym.evalf(subs=bindings))
            b_t = float(b_t_sym.evalf(subs=bindings))
            q_t = float(q_t_sym.evalf(subs=bindings))

            steps[t] = -(q_t * b_t)
            cost = q_t + cost * a_t

        # Line search
        alpha = 100
        old_Ps = sim.Ps
        while True:
            Ps = []
            for t in range(len(ds)):
                Ps.append(old_Ps[t] + alpha * steps[t])
            sim.forward(Ps, params)

            power_scale = args.power / sim.get_average_power()
            for t in range(len(ds)):
                sim.Ps[t] *= power_scale
            sim.forward(sim.Ps, params)

            if sim.get_total_time() < last_time:
                break
            else:
                alpha /= 10
                if alpha < 1e-6:
                    print("Line search broken")

        print(
            f"\nTotal time:\t\t{datetime.timedelta(seconds=int(sim.get_total_time()))}\n"
            f"Total distance:\t{sim.get_total_distance() / 1000:.3f}km\n"
            f"Avg. Speed:\t\t{sim.get_average_speed() * 3.6:.1f}km/h\n"
            f"Work:\t\t\t{sim.get_total_work() / 1000:.0f}kJ ({sim.get_average_power():.0f}W Avg)\n"
            f"Vertical:\t\t+{sim.get_vertical_meters()[0]:.0f}m, -{sim.get_vertical_meters()[1]:.0f}m")

    print("\nPacing Plan:")
    for t in range(len(ds)):
        print(f"{sim.ts[t]:.0f}s ({sim.ds[t]:.0f}m) at {sim.Ps[t]:.0f}W ({sim.delta_hs[t] / sim.ds[t] * 100:.1f}%)")


if __name__ == "__main__":
    main()
