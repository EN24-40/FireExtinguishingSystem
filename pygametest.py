import pygame
from gpiozero import PWMLED
import time
import smbus
import math
import matplotlib.pyplot as plt

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

pin_pwm = PWMLED(20)
pin_dir = PWMLED(21)

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
    left_stick_horizontal = joystick.get_axis(0)
    if abs(left_stick_horizontal) > 0.3:
        write_pwm(left_stick_horizontal, pin_pwm, pin_dir)
    else:
        write_pwm(0, pin_pwm, pin_dir)
    
    time.sleep(0.1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
pygame.quit()
