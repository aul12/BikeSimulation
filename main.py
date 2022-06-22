import datetime

import GpxReader
import Simulation

params = {
    "rho": 1.2041,
    "CdA": 0.25,
    "Crr": 0.002845,
    "m": 72,
    "g": 9.81,
}

target = 260

ds, delta_hs = GpxReader.read_gpx("Walchsee.gpx")

sim = Simulation.Simulation(ds, delta_hs)
sim.Ps = [300] * len(ds)

for i in range(1000):
    sim.forward(sim.Ps, params)

    # Gradient descend step
    dvelocity_dpowers = sim.dvelocity_dpower(sim.Ps, params)
    for t in range(len(sim.Ps)):
        sim.Ps[t] += 1000 * dvelocity_dpowers[t]

    # Renormalize to fix average
    normalize_scale = target / sim.get_average_power()
    for t in range(len(sim.Ps)):
        sim.Ps[t] *= normalize_scale

print(
    f"Total time: {datetime.timedelta(seconds=sim.get_total_time())}, "
    f"Total distance: {sim.get_total_distance() / 1000}km, "
    f"Avg. Speed: {sim.get_average_speed() * 3.6}km/h, "
    f"Work: {sim.get_total_work() / 1000}kJ ({sim.get_average_power()}W Avg),"
    f"Vertical: +{sim.get_vertical_meters()[0]}, -{sim.get_vertical_meters()[1]}")

for t in range(len(sim.Ps)):
    print(f"{sim.ts[t]}s at {sim.Ps[t]}W ({sim.delta_hs[t] / sim.ds[t] * 100}%, {sim.vs[t] * 3.6}km/h)")
