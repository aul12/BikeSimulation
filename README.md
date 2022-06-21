# Optimal Bike Split
Definitely not a copy of bestbikesplit.

# Theory
A given route is split into segments (for example between GPX waypoints),
for every segment a constant power and constant gradient is assumed.
Given the velocity at the beginning of the segment and the power the velocity
at the end of the segment can be calculated. This gives the time for each
segment and thus the overall time. This overall time is minimized with respect
to the power, constraining the average power to the desired value.

## Nomenclature
### Variables
 * $v_{k+1}$: velocity when entering the segment
 * $v_k$: velocity when leaving the segment
 * $\bar{v}$ average velocity for the segment
 * $d$: distance of the segment
 * $\Delta h$: difference in altitude in the segment
 * $P$: Power
 * $W$: Work

### Parameters
 * $\rho$: Air Density
 * $CdA$: Effective frontal area (frontal area times coefficient of drag)
 * $Crr$: Coefficient of rolling resistance
 * $m$: System mass
 * $g$: Gravitational constant

## Physics
There are four important losses to consider: climbing, accelerating,
aerodynamic drag and rolling resistance.

The energy spent for each of the losses is given by:
$$
W_\text{Climbing} = m g \Delta h
$$
$$
W_\text{Accelerating} = 