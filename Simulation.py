import math


class Simulation:
    def __init__(self, ds: list, delta_hs: list):
        assert len(ds) == len(delta_hs)
        self.ds = ds
        self.delta_hs = delta_hs

        self.vs = []
        self.Ps = []
        self.ts = []

    def forward(self, Ps: list, params: dict, initial_velocity=5):
        assert len(Ps) == len(self.ds)
        self.Ps = Ps

        rho = params["rho"]
        CdA = params["CdA"]
        Crr = params["Crr"]
        m = params["m"]
        g = params["g"]

        last_velocity = initial_velocity

        for i in range(len(self.Ps)):
            delta_h = self.delta_hs[i]
            d = self.ds[i]
            P = self.Ps[i]

            while True:
                arg = -2 * g * delta_h + last_velocity ** 2 - 1 / m * rho * last_velocity ** 2 * CdA * d - 2 * g * Crr + P * 2 * d / (
                        m * last_velocity)
                if arg >= 0:
                    break
                else:
                    self.Ps[i] += 10

            v = math.sqrt(arg)
            t = d / last_velocity

            self.vs.append(v)
            self.ts.append(t)
            last_velocity = v

    def get_total_time(self):
        total_time = 0
        for t in self.ts:
            total_time += t

        return total_time

    def get_total_distance(self):
        total_distance = 0
        for d in self.ds:
            total_distance += d

        return total_distance

    def get_total_work(self):
        work = 0
        for P, t in zip(self.Ps, self.ts):
            work += P * t

        return work

    def get_average_speed(self):
        return self.get_total_distance() / self.get_total_time()

    def get_average_power(self):
        return self.get_total_work() / self.get_total_time()
