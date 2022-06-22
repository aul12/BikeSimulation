# Bike Simulation
Simulation of bike dynamics

# Theory
A given route is split into segments (for example between GPX waypoints),
for every segment a constant power and constant gradient is assumed.
Given the velocity at the beginning of the segment and the power the velocity
at the end of the segment can be calculated. This gives the time for each
segment and thus the overall time. This overall time is minimized with respect
to the power, constraining the average power to the desired value.

## Physics
There are four important losses to consider: climbing, accelerating,
aerodynamic drag and rolling resistance. All energy that is produced is given by the rider, this allows to formulate
the dynamics using the laws of energy conservation:

$$
W_\text{Climbing} + W_\text{Accelerating} + W_\text{Drag} + W_\text{Roll} = W_\text{Rider}
$$

The energy spent for each of the losses is given by (for the drag and time calculation the velocity at the beginning at the segment is taken,
if the difference in velocity in the segment is large this approximation might yield problems):

$$
W_\text{Climbing} = m g \Delta h
$$

$$
W_\text{Accelerating} = \frac{1}{2} m (v_k^2 - v_{k-1}^2)
$$

$$
W_\text{Drag} = \frac{1}{2} \rho v_{k-1}^2 CdA d
$$

$$
W_\text{Roll} = m g Crr
$$

The energy injected into the system is given by the power produced by the rider over the duration:

$$
W_\text{Rider} = P t
$$

the time is given by the distance of the segment and the average velocity

$$
t = \frac{d}{v_{k-1}}
$$

Combining all of the equations from above one arrives at:

$$
m g \Delta h + \frac{1}{2} m (v_k^2 - v_{k-1}^2) +  \frac{1}{2} \rho v_{k-1}^2 CdA d +  m g Crr = P \frac{d}{v_{k-1}}
$$

which can be solved for $v_k$:

$$ 
\sqrt{-2 g \Delta h + v_{k-1}^2 - \frac{1}{m} \rho v_{k-1}^2 CdA d - 2 g Crr + P \frac{2 d}{m v_{k-1}}} = v_k
$$

which then allows for the calculation of $t$ and thus the overall time.

## Nomenclature
### Variables
 * $v_{k-1}$: velocity when entering the segment
 * $v_k$: velocity when leaving the segment
 * $d$: distance of the segment
 * $t$: Time required for the segment
 * $\Delta h$: difference in altitude in the segment
 * $P$: Power
 * $W$: Work

### Parameters
 * $\rho$: Air Density
 * $CdA$: Effective frontal area (frontal area times coefficient of drag)
 * $Crr$: Coefficient of rolling resistance
 * $m$: System mass
 * $g$: Gravitational constant

