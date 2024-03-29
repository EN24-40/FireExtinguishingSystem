from gpiozero import PWMLED
import time
import smbus
import math
import matplotlib.pyplot as plt

# Set PWM pins
pin_pwm = PWMLED(20)
pin_dir = PWMLED(21)

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

    if channel == 0:
        min_value = 950
        max_value = 21827
        offset = 1.250
        stroke = 6

    if channel == 1:
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
SP = float(input("set point (in): "))
thresh = 0.002

lower = SP - thresh
upper = SP + thresh

e = 0
e_prev = 0

count = 0

start_time = time.time()
act_meas = 0

for i in range(200):
        prev_meas = act_meas
        act_ana, act_voltage, act_meas = read_ads1115(1)
        # This command will be changed to fit with the function definition in adctest.py

        if ((prev_meas > SP) and (act_meas < SP)) or ((prev_meas < SP) and (act_meas > SP)):
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


        if SP > offset + 6:
            SP = offset + 6
        if SP < offset:
            SP = offset

        e_prev = e		# Added

        e = SP - act_meas

        # Added PID Specific Code
        integral += e * Ts
        deriv = (e - e_prev) / Ts

        data.append(act_meas)
        times.append(time.time() - start_time)

        u = Kp * e

        write_pwm(u,pin_pwm, pin_dir)

        time.sleep(Ts)

pin_dir.value = 0
pin_pwm.value = 0
pin_dir.off()
pin_pwm.off()

plt.title(f"Step Response of Linear Actuator, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
plt.ylabel("Length (in)")
plt.xlabel("Time (sec)")
plt.plot(times, data, linewidth=1.0)
plt.savefig("stepresponse.png")


plt.title(f"Step Response of Linear Actuator, Kp = {Kp}, Ki = {Ki}, Kd = {Kd}")
plt.ylabel("Length (in)")
plt.xlabel("Time (sec)")
plt.plot(times, data, linewidth=1.0)
plt.ylim([SP-0.05, SP+0.05])
plt.xlim([times[math.floor(len(times)/2)],times[len(times)-1]])
plt.savefig("stepresponsezoom.png")