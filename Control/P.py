from gpiozero import PWMLED
import time

pin_out = PMWLED(20)
pin_in = PMWLED(21)

# Sample Parameters
Kp = 0.8
Ts = 0.01
SP = 5


# Sample every Ts seconds:
if (time == Ts):
    time = time - Ts
#    act_meas = readADC()

    e = SP - act_meas

    u = e * Kp

#    writeDA(u)
