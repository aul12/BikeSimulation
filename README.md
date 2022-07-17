# Bike Simulation

Physics based simulation of bike velocity considering climbing, aerodynamics
and rolling resistance. Enables the calculation of many values:

* CdA from a recorded activity
* Power estimation from a time for a given segment
* Optimal pacing


## CdA Estimation

Using the physics (see below) the CdA can be estimated from a recorded activity. For every timestep
the power used for climbing, accelerating and the rolling resistance is calculated. Subtracting this power from the
power produced by the rider yields the power lost to drag

$$
P_\text{Rider}(t) - P_\text{Climbing}(t) - P_\text{Accelerating}(t) - P_\text{Roll} = P_\text{Drag}
$$

over all data points (consisting of velocity and corresponding drag) the CdA can be estimated through a least squares
fit.

Run `python3 CdAEstimation.py --help` to get more information on the usage of the tool.

## Optimal Pacing

Optimizes the total time for a course for a given average power. For this the pacing strategy is formulated as an 
optimal control problem with the velocity dynamics as described below. This optimal control problem is solved using
a model predictive controller based on dynamic gradient descend.

Run `python3 OptimalPacing.py --help` to get more information on the usage of the tool.

## Theory

A given route is split into segments (for example between GPX waypoints),
for every segment a constant gradient is assumed.
Given the velocity at the beginning of the segment and the power the velocity
over the segment can be calculated. This gives the time for each
segment and thus the overall time. For the optimal pacing this overall time is minimized with respect
to the power, constraining the average power to the desired value.

### Physics

There are four important losses to consider: climbing, accelerating,
aerodynamic drag and rolling resistance. All power that is produced is given by the rider, this allows to formulate
the dynamics using the laws of energy conservation:

$$
P_\text{Climbing}(t) + P_\text{Accelerating}(t) + P_\text{Drag}(t) + P_\text{Roll}(t) = P_\text{Rider}(t)
$$

The power lost for each of the losses is given by:

$$
P_\text{Climbing} = m g \dot{h(t)} = m g \frac{\Delta h}{d} v(t)
$$

$$
P_\text{Accelerating} = m v(t) \dot{v(t)}
$$

$$
P_\text{Drag} = \frac{1}{2} \rho {v(t)}^3 C_\text{d}A
$$

$$
P_\text{Roll} = m g C_\text{rr} v(t)
$$

The power of the rider over the segment is assumed to be constant:

$$
P_\text{Rider}(t) = P
$$

Combining all the equations from above one arrives at:

$$
m g \frac{\Delta h}{d} v(t) + m v(t) \dot{v(t)} + \frac{1}{2} \rho {v(t)}^3 C_\text{d}A + m g C_\text{rr} v(t) = P
$$

which can be reformulated as

$$
P \frac{1}{m v(t)} - g (\frac{\Delta h}{d} + C_\text{rr}) - \frac{1}{2 m} \rho C_\text{d}A {v(t)}^2 = \dot{v(t)}
$$

a solution to this non-linear differential equation can be approximated using numerical algorithms.

### Nomenclature

#### Variables

* $v(t)$: velocity
* $d$: distance of the segment
* $\Delta h$: difference in altitude in the segment
* $P$: Power

#### Parameters

* $\rho$: Air Density
* $C_\text{d}A$: Effective frontal area (frontal area times coefficient of drag)
* $C_\text{rr}$: Coefficient of rolling resistance
* $m$: System mass
* $g$: Gravitational constant
