from gpiozero import PWMLED
import time
import smbus

# Set PWM pins
pin_ret = PMWLED(20)
pin_ext = PMWLED(21)

# ADS1115 default address
ADS1115_ADDRESS = 0x48

# ADS1115 registers
ADS1115_CONVERSION = 0x00
ADS1115_CONFIG = 0x01

# Configuration settings
ADS1115_CONFIG_OS_SINGLE = 0x8000
ADS1115_CONFIG_MUX_SINGLE_0 = 0x4000  # Channel 0
ADS1115_CONFIG_GAIN = 0x0200  # +/-4.096V
ADS1115_CONFIG_MODE_SINGLE = 0x0100  # Single-shot mode
ADS1115_CONFIG_DR_860SPS = 0x0080  # 860 samples per second
ADS1115_CONFIG_CMODE_TRAD = 0x0000  # Traditional comparator
ADS1115_CONFIG_CPOL_ACTVLOW = 0x0000  # Active low
ADS1115_CONFIG_CLAT_NONLAT = 0x0000  # Non-latching
ADS1115_CONFIG_CQUE_NONE = 0x0003  # Disable comparator

bus = smbus.SMBus(1)

def read_ads1115(channel):
    # Configuring the ADC
    config = (ADS1115_CONFIG_OS_SINGLE |
              ADS1115_CONFIG_MUX_SINGLE_0 |
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

    inches = 0.75 + (value-778) / 21827 * 6
    if inches > 6.75:
        inches = 6.75
    if inches < 0:
        inches = 0

    return value, voltage, inches

def write_pwm(u,SP):
    if u < SP:
        pin_ext.value = 1
    if u > SP:
        pin_ret.value = 1



# Sample Parameters (will be changed before and after tuning)
Kp = 0.8
Ki = 2
Kd = 3
Ts = 0.01
SP = 5

lower = SP - (0.05*SP)
upper = SP + (0.05*SP)

k1 = Kp + Ki + Kd
k2 = (-1*Kp) - (2*Kd)
k3 = Kd

u_prev = 0
u = 0
e = 0
e1 = 0
e2 = 0

on = 1

while on:
    # Reset error values:
    e2 = e1
    e1 = e
    u_prev = u

    act_ana, act_voltage, act_meas = read_ads1115(0)
    # This command will be changed to fit with the function definition in adctest.py

    e = SP - act_meas

    u = u_prev + (e*k1) + (e1*k2) + (e2*k3)

    if act_meas < SP

    write_pwm(u,SP)
    # This command will also be changed to fit with the function definition in adctest.py

    time.sleep(Ts-0.002)

    # Exit if within threshold
    if (u>lower) & (u<upper):
        on = 0