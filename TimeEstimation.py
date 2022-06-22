import datetime

from lib import GpxReader, Simulation, ParamReader

target = 300

params = ParamReader.read_params("params.json")
ds, delta_hs = GpxReader.read_gpx("Hagebuchen.gpx")

sim = Simulation.Simulation(ds, delta_hs)
sim.Ps = [300] * len(ds)
sim.forward(sim.Ps, params)

print(
    f"Total time: {datetime.timedelta(seconds=sim.get_total_time())}, "
    f"Total distance: {sim.get_total_distance() / 1000}km, "
    f"Avg. Speed: {sim.get_average_speed() * 3.6}km/h, "
    f"Work: {sim.get_total_work() / 1000}kJ ({sim.get_average_power()}W Avg),"
    f"Vertical: +{sim.get_vertical_meters()[0]}, -{sim.get_vertical_meters()[1]}")



