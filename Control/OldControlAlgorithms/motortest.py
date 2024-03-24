from gpiozero import PWMLED
import time

# Set up the GPIO pins
pin_w = PWMLED(21)  # for 'w' key
pin_s = PWMLED(20)  # for 's' key

try:

    print("extending")
    
    pin_w.value = 1
    time.sleep(3)

    pin_w.off()

    time.sleep(1)

    print("retracting")

    
    pin_s.value = 1
    time.sleep(3)

    pin_s.off()

    time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO state
    pin_w.value = 0
    pin_w.value = 0
    pin_w.off()
    pin_s.off()
    print("\nScript terminated by user.")