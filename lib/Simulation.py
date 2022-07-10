from enum import Enum

import matplotlib.pyplot as plt
from .SqrtWrapper import sqrt


class Solver(Enum):
    SHOOTING = 1,


class Simulation:

    def __init__(self, ds: list, delta_hs: list):
        assert len(ds) == len(delta_hs)
        self.ds = ds
        self.delta_hs = delta_hs

        self.vs = []
        self.Ps = []
        self.ts = []

    def get_acceleration(self, v, P, d: float, delta_h: float, params: dict):
        rho = params["rho"]
        CdA = params["CdA"]
        Crr = params["Crr"]
        m = params["m"]
        g = params["g"]

        return P / (m * v) - g * (delta_h / d + Crr) - 1 / (2 * m) * rho * CdA * v ** 2

    def get_velocity(self, last_velocity, P, d: float, delta_h: float, params: dict, solver=Solver.SHOOTING):
        if solver == Solver.SHOOTING:
            acceleration = self.get_acceleration(last_velocity, P, d, delta_h, params)

            # Physics:
            #      s = v_0 * t + 0.5 * a * t^2
            #
            # Quadratic equation with:
            #      A = 0.5 * a
            #      B = v_0
            #      C = -s
            #
            #      t = (-v_0 +- sqrt(v_0^2 + 2 * s * a)) / a
            # If a > 0 the sqrt is larger than v_0, thus the only possible solution is ...+sqrt()
            #
            # For a < 0 the sqrt is less than v_0 as the rider decelerates, gets to the distance, overshoots and
            # drives back, thus we select the smaller time which is also ...+sqrt()
            #
            # Notes regarding the argument of the sqrt: if we stop (and reverse) before travelling the given distance
            # the solution becomes useless.
            #

            t = (-last_velocity + sqrt(last_velocity ** 2 + 2 * d * acceleration)) / acceleration
            return last_velocity + acceleration * t
        else:
            raise "Unknown solver!"

    def forward(self, Ps: list, params: dict, initial_velocity=5):
        assert len(Ps) == len(self.ds)
        self.Ps = Ps
        self.vs = [initial_velocity]
        self.ts = []

        for i in range(len(self.Ps)):
            delta_h = self.delta_hs[i]
            d = self.ds[i]
            P = self.Ps[i]

            while True:
                try:
                    v = self.get_velocity(self.vs[-1], P, d, delta_h, params)
                except ValueError:
                    # Overpower required
                    self.Ps[i] += 10
                    P = self.Ps[i]
                    continue
                break

            t = d / self.vs[-1]

            self.vs.append(v)
            self.ts.append(t)

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

    def get_vertical_meters(self):
        vert_pos = 0
        vert_neg = 0
        for delta_h in self.delta_hs:
            if delta_h > 0:
                vert_pos += delta_h
            else:
                vert_neg -= delta_h

        return vert_pos, vert_neg

    def plot(self, show_speed=False, show_power=False, show_elevation=False):
        xs = [0]
        for x in self.ds:
            xs.append(xs[-1] + x / 1000)

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        assert show_speed or show_power

        if show_speed:
            vs_kmh = [v * 3.6 for v in self.vs]
            ax1.plot(xs, vs_kmh, color="green")
            ax1.set_ylabel("Speed (km/h)", color="green")

        if show_power:
            ax2.plot(xs[1:], self.Ps, color="red")
            ax2.set_ylabel("Power (W)", color="red")

        if show_elevation:
            hs = [0]
            for delta_h in self.delta_hs:
                hs.append(hs[-1] + delta_h)

            ax = ax1 if show_speed else ax2
            min_y, max_y = ax.get_ylim()

            min_h = min(hs)
            max_h = max(hs)

            hs = [(h - min_h) / (max_h - min_h) * (max_y - min_y) + min_y for h in hs]

            ax.plot(xs, hs, color="gray")

        plt.show()
