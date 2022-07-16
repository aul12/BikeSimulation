import argparse
import copy
import datetime
import math
import sys

import sympy

from lib import GpxReader, FitReader, Simulation, ParamReader, RouteNormalization, ElevationSmoothing


def main():
    parser = argparse.ArgumentParser("Estimate the optimal power profile for a course")
    parser.add_argument("file", metavar="F", type=str,
                        help="The gpx file of the course")
    parser.add_argument("--params", dest="params", type=str, help="Params file", default="params.json")
    parser.add_argument("--power", dest="power", type=float, help="Average Power (in Watts) for the course",
                        default=300)
    parser.add_argument("--max_power", dest="max_power", type=float, help="Max Power (in Watts) for the course",
                        default=700)
    parser.add_argument("--segment_len", dest="segment_len", type=float, help="Length of a segment over which constant"
                                                                              "power is assumed", default=1)
    parser.add_argument("--elevation_smooth_window", dest="elevation_smooth_window", type=float,
                        help="Size of the window used for elevation smoothing", default=50)
    parser.add_argument("--elevation_smooth_std_dev", dest="elevation_smooth_std_dev", type=float,
                        help="Standard deviation of the kernel used for elevation smoothing", default=50)
    parser.add_argument("--initial_velocity", dest="init_vel", type=float,
                        help="Initial velocity (in km/h), needs to be positive", default=30)
    parser.add_argument("--max_iterations", dest="max_iterations", type=int,
                        help="Maximum optimizer iterations", default=100)
    parser.add_argument("--power_tolerance", dest="power_tolerance", type=float,
                        help="Maximum deviation from average to accept pacing strategy", default=5)
    parser.add_argument("--time_tolerance", dest="time_tolerance", type=float,
                        help="Improvement in time at which to stop optimization", default=0.5)

    args = parser.parse_args()

    params = ParamReader.read_params(args.params)
    if args.file.endswith(".gpx"):
        ds, delta_hs = GpxReader.read_gpx(args.file)
    elif args.file.endswith(".fit"):
        ds, delta_hs, _, _ = FitReader.read_fit(args.file)
    else:
        print("Unknown file format!")
        sys.exit(1)
    ds, delta_hs = RouteNormalization.normalize(ds, delta_hs, segment_len=args.segment_len)
    ds, delta_hs = ElevationSmoothing.smooth_truncated_gaussian(ds, delta_hs, width=args.elevation_smooth_window,
                                                                sigma=args.elevation_smooth_std_dev)

    init_velocity = args.init_vel / 3.6
    assert init_velocity > 0

    sim_solver = Simulation.Solver.TIME_EULER
    sim_solver_params = {"distance_euler_step_size": 1,
                         "time_euler_step_size": 0.1,
                         "min_time_euler_step_size": 0.01}

    sim = Simulation.Simulation(ds, delta_hs)
    sim.forward([args.power] * len(ds), initial_velocity=init_velocity, params=params, solver=sim_solver,
                solver_params=sim_solver_params)
    last_time = sim.get_total_time()
    print(f"[Step 0]\tTotal time:\t\t{datetime.timedelta(seconds=int(last_time))}", end="")

    # System description:
    #   v_{t+1} = f(v_t, P_t)
    # State cost = t = d/v_t, Control Cost = 0
    v_t, P_t, d_t, delta_h_t = sympy.symbols("v_t, P_t, d_t, delta_h_t")
    f = sim.get_velocity(last_velocity=v_t, P=P_t, d=d_t, delta_h=delta_h_t, params=params,
                         solver=Simulation.Solver.DIRECT_SHOOTING)
    a_t_sym = f.diff(v_t)
    b_t_sym = f.diff(P_t)

    state_cost_sym = d_t / v_t
    q_t_sym = state_cost_sym.diff(v_t)

    for c in range(args.max_iterations):
        # Run once with direct shooting to have an appropriate over power for solver for step
        if sim_solver != Simulation.Solver.DIRECT_SHOOTING:
            sim.forward([args.power] * len(ds), initial_velocity=init_velocity, params=params,
                        solver=Simulation.Solver.DIRECT_SHOOTING)

        # Back pass
        cost = float(q_t_sym.evalf(subs={
            v_t: sim.vs[-1],
            P_t: sim.Ps[-1],
            d_t: ds[-1],
            delta_h_t: delta_hs[-1]
        }))
        steps = [0] * len(ds)
        for i in range(len(ds)):
            t = len(ds) - i - 1

            bindings = {
                v_t: sim.vs[t],
                P_t: sim.Ps[t],
                d_t: ds[t],
                delta_h_t: delta_hs[t]
            }

            a_t = float(a_t_sym.evalf(subs=bindings))
            b_t = float(b_t_sym.evalf(subs=bindings))
            q_t = float(q_t_sym.evalf(subs=bindings))

            steps[t] = -(cost * b_t)
            cost = q_t + cost * a_t

        # Line search
        best_time = math.inf
        old_Ps = copy.deepcopy(sim.Ps)
        best_powers = None

        for alpha_exp in range(-10, 6):
            alpha = 10 ** alpha_exp

            # Apply step
            for t in range(len(ds)):
                sim.Ps[t] = min(max(old_Ps[t] + alpha * steps[t], 0), args.max_power)

            # Reforward to get average (depends on time for each segment)
            sim.forward(sim.Ps, params, initial_velocity=init_velocity, solver=sim_solver,
                        solver_params=sim_solver_params)

            # Rescale average
            power_scale = args.power / sim.get_average_power()
            for t in range(len(ds)):
                sim.Ps[t] *= power_scale

            # Reforward to recompute velocity
            sim.forward(sim.Ps, params, initial_velocity=init_velocity, solver=sim_solver,
                        solver_params=sim_solver_params)

            if sim.get_total_time() < best_time:
                best_time = sim.get_total_time()
                best_powers = copy.deepcopy(sim.Ps)

        # Update internal state of sim...
        sim.forward(copy.deepcopy(best_powers), params=params, solver=sim_solver, solver_params=sim_solver_params,
                    initial_velocity=init_velocity)

        if abs(sim.get_total_time() - last_time) < args.time_tolerance \
                and sim.get_average_power() < args.power + args.power_tolerance:
            break
        else:
            last_time = sim.get_total_time()
            print(f"\r[Step {c + 1}]\tTotal time:\t\t{datetime.timedelta(seconds=int(last_time))}", end="")

    print(
        f"\rTotal time:\t\t{datetime.timedelta(seconds=int(last_time))}\n"
        f"Total distance:\t{sim.get_total_distance() / 1000:.3f}km\n"
        f"Avg. Speed:\t\t{sim.get_average_speed() * 3.6:.1f}km/h\n"
        f"Work:\t\t\t{sim.get_total_work() / 1000:.0f}kJ ({sim.get_average_power():.0f}W Avg)\n"
        f"Vertical:\t\t+{sim.get_vertical_meters()[0]:.0f}m, -{sim.get_vertical_meters()[1]:.0f}m")

    print("\nPacing Plan:")
    for t in range(len(ds)):
        print(f"{sim.ts[t]:.1f}s ({sim.ds[t]:.0f}m) at {sim.Ps[t]:.0f}W ({sim.delta_hs[t] / sim.ds[t] * 100:.1f}%, "
              f"{sim.vs[t] * 3.6:.1f}km/h)")

    sim.plot(show_speed=True, show_power=True, show_elevation=True, show_average_power=True,
             title=f"Optimal pacing for {args.file}")


if __name__ == "__main__":
    main()
