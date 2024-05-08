import pygame
from gpiozero import PWMLED
import time
import smbus
import math
import matplotlib.pyplot as plt

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

# Limits
yaw_min_digital = 2850
yaw_max_digital = 17150
pitch_min_digital = 9000
pitch_max_digital = 22640

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

    #M2, Pitch
    if channel == 1:
        min_value = 950
        max_value = 21827
        offset = 1.250
        stroke = 6

    #M1, Yaw
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

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

#M2
pitch_pwm = PWMLED(19)
pitch_dir = PWMLED(26)

#M1
yaw_pwm = PWMLED(20)
yaw_dir = PWMLED(21)

def write_pwm(u, pin_p, pin_d):
    d = 0
    if u < 0:
        d = 1
    
    pin_d.value = d

    u_s = abs(u)

    if u_s > 1:
        u_s = 1
    
    pin_p.value = u_s

# Wait for a joystick to be connected
while pygame.joystick.get_count() == 0:
    pygame.event.pump()
    print("Please connect a PS4 controller...")
    pygame.time.wait(1000)

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Detected joystick: {joystick.get_name()}")



# Main loop
running = True
while running:
    pygame.event.pump()  # Update Pygame's internal event queue
    # Get the left stick's horizontal movement
    for i in range(5):
        read_ads1115(0)
    yaw_digital_value, yaw_voltage, yaw_inches = read_ads1115(0)
    for i in range(5):
        read_ads1115(1)
    pitch_digital_value, pitch_voltage, pitch_inches = read_ads1115(1)


    print((yaw_inches-4.0909)/-0.0517)

    left_stick_horizontal = joystick.get_axis(0)
    if abs(left_stick_horizontal) > 0.3:
        if ((left_stick_horizontal > 0) and (yaw_digital_value <= yaw_min_digital)) or ((left_stick_horizontal < 0) and (yaw_digital_value >= yaw_max_digital)):
            write_pwm(0, yaw_pwm, yaw_dir)
        else:
            write_pwm(-left_stick_horizontal, yaw_pwm, yaw_dir)
    else:
        write_pwm(0, yaw_pwm, yaw_dir)

    
    #print(round(yaw_inches, 3))

    right_stick_vertical = joystick.get_axis(3)
    if abs(right_stick_vertical) > 0.3 and abs(left_stick_horizontal) < 0.3:
        if ((right_stick_vertical < 0) and (pitch_digital_value >= pitch_max_digital)) or ((right_stick_vertical > 0) and (pitch_digital_value <= pitch_min_digital)):
            write_pwm(0, pitch_pwm, pitch_dir)
        else:
            write_pwm(-right_stick_vertical, pitch_pwm, pitch_dir)
    else:
        write_pwm(0, pitch_pwm, pitch_dir)
    
    time.sleep(0.1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
write_pwm(0, yaw_pwm, yaw_dir)
write_pwm(0, pitch_pwm, pitch_dir)
pitch_dir.off()
pitch_pwm.off()
yaw_dir.off()
yaw_pwm.off()
pygame.quit()
