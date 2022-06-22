import datetime

from lib import FitReader, Simulation, ParamReader

target = 300

params = ParamReader.read_params("params.json")
ds, delta_hs, Ps, real_total_time = FitReader.read_fit("Gz_Ns.fit")

sim = Simulation.Simulation(ds, delta_hs)


lower_bound = 0
upper_bound = 1

while abs(upper_bound-lower_bound) > 0.0001:
    mid = (upper_bound+lower_bound)/2
    params["CdA"] = mid

    sim.forward(Ps, params)

    if sim.get_total_time() > real_total_time:
        # reduce cda
        upper_bound = mid
    else:
        lower_bound = mid

    print(f"Trying CdA: {mid} (upper: {upper_bound}, lower: {lower_bound})")


print(
    f"Simulated Total time: {datetime.timedelta(seconds=sim.get_total_time())}, "
    f"Real Total time: {datetime.timedelta(seconds=real_total_time)}, "
    f"Total distance: {sim.get_total_distance() / 1000}km, "
    f"Avg. Speed: {sim.get_average_speed() * 3.6}km/h, "
    f"Work: {sim.get_total_work() / 1000}kJ ({sim.get_average_power()}W Avg),"
    f"Vertical: +{sim.get_vertical_meters()[0]}, -{sim.get_vertical_meters()[1]}")