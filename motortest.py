from gpiozero import PWMLED
import keyboard
import time

# Set up the GPIO pins
pin_w = PWMLED(21)  # for 'w' key
pin_s = PWMLED(20)  # for 's' key

try:
    while True:
        
        for i in range(50):
            pin_w.value = i / 50
            time.sleep(0.1)

        pin_w.off()

        for i in range(50):
            pin_s.value = i / 50
            time.sleep(0.1)

        pin_s.off()

except KeyboardInterrupt:
    # Clean up GPIO state
    pin_w.off()
    pin_s.off()
    print("\nScript terminated by user.")
