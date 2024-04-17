from gpiozero import PWMLED
import time
import smbus
import math
import matplotlib.pyplot as plt
import sympy as sp

#M2
pitch_pwm = PWMLED(19)
pitch_dir = PWMLED(26)

#M1
yaw_pwm = PWMLED(20)
yaw_dir = PWMLED(21)

offset = 1.25

data = []
times = []

# ADS1115 default address
ADS1115_ADDRESS = 0x48

# ADS1115 registers
ADS1115_CONVERSION = 0x00
ADS1115_CONFIG = 0x01

# Configuration settings
ADS1115_CONFIG_OS_SINGLE = 0x8000
ADS1115_CONFIG_MUX_SINGLE_0 = 0x4000  # Channel 0
ADS1115_CONFIG_MUX_SINGLE_1 = 0x5000  # Channel 1
ADS1115_CONFIG_MUX_SINGLE_2 = 0x6000  # Channel 2
ADS1115_CONFIG_MUX_SINGLE_3 = 0x7000  # Channel 3
ADS1115_CONFIG_GAIN = 0x0200  # +/-4.096V
ADS1115_CONFIG_MODE_SINGLE = 0x0100  # Single-shot mode
ADS1115_CONFIG_DR_860SPS = 0x0080  # 860 samples per second
ADS1115_CONFIG_CMODE_TRAD = 0x0000  # Traditional comparator
ADS1115_CONFIG_CPOL_ACTVLOW = 0x0000  # Active low
ADS1115_CONFIG_CLAT_NONLAT = 0x0000  # Non-latching
ADS1115_CONFIG_CQUE_NONE = 0x0003  # Disable comparator

# Initialize I2C (SMBus)
bus = smbus.SMBus(1)

def read_ads1115(channel):
    # Configuring the ADC
    config = (ADS1115_CONFIG_OS_SINGLE |
              {0: ADS1115_CONFIG_MUX_SINGLE_0, 1: ADS1115_CONFIG_MUX_SINGLE_1,
               2: ADS1115_CONFIG_MUX_SINGLE_2, 3: ADS1115_CONFIG_MUX_SINGLE_3}[channel] |
              ADS1115_CONFIG_GAIN |
              ADS1115_CONFIG_MODE_SINGLE |
              ADS1115_CONFIG_DR_860SPS |
              ADS1115_CONFIG_CMODE_TRAD |
              ADS1115_CONFIG_CPOL_ACTVLOW |
              ADS1115_CONFIG_CLAT_NONLAT |
              ADS1115_CONFIG_CQUE_NONE)

    # Write config register to the ADC
    bus.write_i2c_block_data(ADS1115_ADDRESS, ADS1115_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])

    # Wait for the ADC conversion to complete
    # The ADS1115 has a maximum conversion time of 1/860 SPS = 1.16ms per sample
    time.sleep(0.002)

    # Read the conversion result
    result = bus.read_i2c_block_data(ADS1115_ADDRESS, ADS1115_CONVERSION, 2)
        # Convert the result to 16 bits and adjust for the configured gain
    value = (result[0] << 8) | (result[1])
    if value & 0x8000 != 0:
        value -= 1 << 16
    voltage = value * 4.096 / 32767.0

    min_value = 0
    max_value = 0
    offset = 0
    stroke = 0

    #M2, Pitch, A1
    if channel == 1:
        min_value = 950
        max_value = 21827
        offset = 1.250
        stroke = 6

    #M1, Yaw, A0
    if channel == 0:
        min_value = 818
        max_value = 22960 - 818
        offset = 1.264
        stroke = 6.087

    inches = offset + (value-min_value) / max_value * stroke
    if inches > offset + stroke:
        inches = offset + stroke
    if inches < 0:
        inches = 0

    return value, voltage, inches

def write_pwm(u, pin_p, pin_d):
    d = 0
    if u < 0:
        d = 1
    
    pin_d.value = d

    u_s = abs(u)

    if u_s > 1:
        u_s = 1
    
    pin_p.value = u_s
        
# Sample Parameters (will be changed before and after tuning)
# Testing had Ku = 12, with Tu = 0.2
Kp = 7.2    #0.6*Ku
Ki = 72		#Kp/0.5*Tu
Kd = 0.18      #0.125*Kp*Tu

# PID Specific Parameters
integral = 0
deriv = 0

Ts = 0.05

# Senior Design Calculations
# Assumptions
# -Ignore head loss
# -Smooth pipes
v1, v2 = sp.symbols('v1 v2')

# Inputs
rho = 1.940 	# slugs/ft^3
g = 32.2 	# ft/s^2
h_sys = 17.625 	# in
pipe_diamter_inlet = 3 	# in
nozzel_diamter = 1.5 		# in

p1 = 25 * 144  	# [lb/ft^2] 
# Given supply pressure, need to verify with fire department what that will be. Assumed 10 psi for now

p2 = 0 * 144  	# [lb/ft^2] outlet atmospheric pressure
friction_losses = 2.2 / 144  # [lb/ft^2] Friction losses in system
y = 0 * 0.3048  	# [m] height of turret

# Calculations

# Diameter Calcs
D1 = pipe_diamter_inlet / 12 	# Ft
D2 = nozzel_diamter / 12 	# Ft

# Area Calcs
A1 = math.pi * D1 ** 2 / 4 	# Area of inlet
A2 = math.pi * D2 ** 2 / 4 	# Area of nozzle

# Convert
Z2 = h_sys / 12 	# Height of system in feet

# Velocity Calculations
E = [sp.Eq(v2, sp.sqrt((2*(p1-p2))/rho + 2*g*(0-Z2) - 2*g*friction_losses + v1**2)),sp.Eq(v1,(A2*v2)/A1)]

S = sp.solve(E, (v1, v2), dict=True)

v1_sol = S[0][v1] 	# [ft/s] Inlet velocity
v2_sol = S[0][v2] 	# [ft/s] Nozzle Velocity
Q = v2_sol * A2 * 448.831 	# [Gal/min] flow rate

# Print v1, v2 and Q:
print(f'v1 = {v1_sol:.3f} ft/s')  	# Print v1
print(f'v2 = {v2_sol:.3f} ft/s')  	# Print v2
print(f'Q = {Q:.3f} Gal/min') 		# Print flow rate Q

# Projectile motion calculations
# Input Range
forward_distance = float(input("forward distance (ft)): "))
side_distance = float(input("side distance (ft), right = +, left = -: "))
R = math.sqrt(forward_distance ** 2 + side_distance ** 2)
print("distance away (ft): ", R)
# Equation for range of turret to solve for theta
# Equation set equal to zero and starts at -60. Loop finds when REQ=0
REQ = -60
# Note: had to switch the range to be in integers for python
for theta_int in range(-9000, 4500):
    theta_d = theta_int / 100
    if REQ >= 0:
        break
    else:
        theta_rad = theta_d * math.pi / 180
        REQ = (-1*R) + (v2_sol * math.cos(theta_rad)) / g * (v2_sol * math.sin(theta_rad) + math.sqrt(v2_sol**2 * math.sin(theta_rad)**2 + 2 * g * y))

theta = theta_rad * 180 / math.pi
print(f"Theta: {theta:.3f} degrees")	# Turret angle in degrees, where 0 deg is level.

angle_pitch = theta

print("pitch ", round(angle_pitch, 3))

angle_yaw = math.degrees(math.atan(side_distance/forward_distance))

print("yaw: ", round(angle_yaw, 3))

if angle_pitch >= -40 and angle_pitch <= 36:
    SP_pitch = 0.0499 * angle_pitch + 5.4249
else:
    SP_pitch = 5.4249
print(SP_pitch)

if angle_yaw >= -31 and angle_yaw <= 43:
    SP_yaw = -0.0517 * angle_yaw + 4.0909
else:
    SP_yaw = 3.9949
print(SP_yaw)



thresh = 0.002
lower = SP_pitch - thresh
upper = SP_pitch + thresh

e = 0
e_prev = 0

count = 0

start_time = time.time()
act_meas = 0

for i in range(200):
        prev_meas = act_meas
        act_dig, act_voltage, act_meas = read_ads1115(1)
        # This command will be changed to fit with the function definition in adctest.py

        if ((prev_meas > SP_pitch) and (act_meas < SP_pitch)) or ((prev_meas < SP_pitch) and (act_meas > SP_pitch)):
            print("cross time = ", time.time()-start_time)


        if act_meas > lower and act_meas < upper:
            count = count + 1
        else:
            count = 0

        if count >= 20:
            print("breaked")
            break

        if act_meas >= offset + 6 or act_meas < offset:
            break


        if SP_pitch > offset + 6:
            SP_pitch = offset + 6
        if SP_pitch < offset:
            SP_pitch = offset

        e_prev = e		# Added

        e = SP_pitch - act_meas

        # Added PID Specific Code
        integral += e * Ts
        deriv = (e - e_prev) / Ts

        data.append(act_meas)
        times.append(time.time() - start_time)

        u = Kp * e

        write_pwm(u,pitch_pwm, pitch_dir)

        time.sleep(Ts)

pitch_dir.value = 0
pitch_pwm.value = 0
pitch_dir.off()
pitch_pwm.off()

time.sleep(0.5)

thresh = 0.002

lower = SP_yaw - thresh
upper = SP_yaw + thresh

e = 0
e_prev = 0
integral = 0
deriv = 0

count = 0

start_time = time.time()
act_meas = 0

for i in range(200):
        prev_meas = act_meas
        act_dig, act_voltage, act_meas = read_ads1115(0)
        # This command will be changed to fit with the function definition in adctest.py

        if ((prev_meas > SP_yaw) and (act_meas < SP_yaw)) or ((prev_meas < SP_yaw) and (act_meas > SP_yaw)):
            print("cross time = ", time.time()-start_time)


        if act_meas > lower and act_meas < upper:
            count = count + 1
        else:
            count = 0

        if count >= 20:
            print("breaked")
            break

        if act_meas >= offset + 6 or act_meas < offset:
            break


        if SP_yaw > offset + 6:
            SP_yaw = offset + 6
        if SP_yaw < offset:
            SP_yaw = offset

        e_prev = e		# Added

        e = SP_yaw - act_meas

        # Added PID Specific Code
        integral += e * Ts
        deriv = (e - e_prev) / Ts

        data.append(act_meas)
        times.append(time.time() - start_time)

        u = Kp * e

        write_pwm(u,yaw_pwm, yaw_dir)

        time.sleep(Ts)

yaw_dir.value = 0
yaw_pwm.value = 0
yaw_dir.off()
yaw_pwm.off()

# plt.title(f"Step Response of Linear Actuator, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
# plt.ylabel("Length (in)")
# plt.xlabel("Time (sec)")
# plt.plot(times, data, linewidth=1.0)
# plt.savefig("stepresponse.png")


# plt.title(f"Step Response of Linear Actuator, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
# plt.ylabel("Length (in)")
# plt.xlabel("Time (sec)")
# plt.plot(times, data, linewidth=1.0)
# plt.ylim([SP-0.05, SP+0.05])
# plt.xlim([times[math.floor(len(times)/2)],times[len(times)-1]])
# plt.savefig("stepresponsezoom.png")