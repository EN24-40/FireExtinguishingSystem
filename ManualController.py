from pyPS4Controller.controller import Controller

# Same setup as PID Controller
from gpiozero import PWMLED
import time
import smbus
import math

# Set PWM pins
pin_ret = PWMLED(20)
pin_ext = PWMLED(21)

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
ADS1115_CONFIG_GAIN = 0x0200  # +/-4.096V
ADS1115_CONFIG_MODE_SINGLE = 0x0100  # Single-shot mode
ADS1115_CONFIG_DR_860SPS = 0x0080  # 860 samples per second
ADS1115_CONFIG_CMODE_TRAD = 0x0000  # Traditional comparator
ADS1115_CONFIG_CPOL_ACTVLOW = 0x0000  # Active low
ADS1115_CONFIG_CLAT_NONLAT = 0x0000  # Non-latching
ADS1115_CONFIG_CQUE_NONE = 0x0003  # Disable comparator

bus = smbus.SMBus(1)


# Same function reading the ADC:
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

    inches = offset + (value-950) / 21827 * 6
    if inches > offset + 6:
        inches = offset + 6
    if inches < 0:
        inches = 0

    return value, voltage, inches


# Manual Controller
class MyController(Controller):

	def __init__(self,**kwargs):
		Controller.__init__(self, **kwargs)

	def on_circle_press(self):
		pin_ext.value = 0.7
		pin_ret.value = 0

	def on_circle_release(self):
		pin_ext.value = 0
		pin_ret.value = 0
		act_ana, act_voltage, act_meas = read_ads1115(0)
		print(act_meas)

	def on_square_press(self):
		pin_ext.value = 0
		pin_ret.value = 0.7

	def on_square_release(self):
		pin_ext.value = 0
		pin_ret.value = 0
		act_ana, act_voltage, act_meas = read_ads1115(0)
		print(act_meas)

# Controller specific code from Github
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
