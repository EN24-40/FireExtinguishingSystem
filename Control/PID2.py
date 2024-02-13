from gpiozero import PWMLED
import time

pin_out = PMWLED(20)
pin_in = PMWLED(21)

# Sample Parameters
Kp = 0.8
Ki = 2
Kd = 3
Ts = 0.01
SP = 5

lower = SP - (0.03*SP)
upper = SP + (0.03*SP)

k1 = Kp + Ki + Kd
k2 = (-1*Kp) – (2*Kd)
k3 = Kd

u_prev = 0
u = 0
e = 0
e1 = 0
e2 = 0

on = 1

while on:
    # Sample every Ts seconds:
    if (time == Ts):
        time = time - Ts

        # Reset error values:
        e2 = e1
        e1 = e
        u_prev = u

#        act_meas = readADC()

        e = SP - act_meas

        u = u_prev + (e*k1) + (e1*k2) + (e2*k3)

#       writeDA(u)

    # Exit if within threshold
    if (u>lower) & (u<upper):
        on = 0
