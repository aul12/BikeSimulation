# Bike Simulation
Physics based simulation of bike velocity considering climbing, aerodynamics
and rolling resistance. Enables the calculation of many values:
 * Time/Speed for a given route with given power
 * CdA from a recorded activity
 * Power estimation from a time for a given segment
 * Optimal pacing (requires precise elevation profile)

## Theory
A given route is split into segments (for example between GPX waypoints),
for every segment a constant power and constant gradient is assumed.
Given the velocity at the beginning of the segment and the power the velocity
at the end of the segment can be calculated. This gives the time for each
segment and thus the overall time. This overall time is minimized with respect
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
P_\text{Drag} = \frac{1}{2} \rho {v(t)}^3 CdA
$$

$$
P_\text{Roll} = m g Crr v(t)
$$

The power of the rider over the segment is assumed to be constant:

$$
P_\text{Rider}(t) = P
$$


Combining all of the equations from above one arrives at:

$$
m g \frac{\Delta h}{d} v(t) + m v(t) \dot{v(t)} + \frac{1}{2} \rho {v(t)}^3 CdA + m g Crr v(t) = P
$$

### Nomenclature
#### Variables
 * $v_{k-1}$: velocity when entering the segment
 * $v_k$: velocity when leaving the segment
 * $d$: distance of the segment
 * $t$: Time required for the segment
 * $\Delta h$: difference in altitude in the segment
 * $P$: Power
 * $W$: Work

#### Parameters
 * $\rho$: Air Density
 * $CdA$: Effective frontal area (frontal area times coefficient of drag)
 * $Crr$: Coefficient of rolling resistance
 * $m$: System mass
 * $g$: Gravitational constant

