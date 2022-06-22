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

ds, delta_hs = GpxReader.read_gpx("Hagebuchen.gpx")
Ps = [300] * len(ds)

sim = Simulation.Simulation(ds, delta_hs)
sim.forward(Ps, params)

print(
    f"Total time: {datetime.timedelta(seconds=sim.get_total_time())}, "
    f"Total distance: {sim.get_total_distance() / 1000}km, "
    f"Avg. Speed: {sim.get_average_speed() * 3.6}km/h, "
    f"Work: {sim.get_total_work() / 1000}kJ ({sim.get_average_power()}W Avg)")
