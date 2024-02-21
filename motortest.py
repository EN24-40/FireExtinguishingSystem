import RPi.GPIO as GPIO
import pigpio
import time

pin_extend = 21  # for 'w' key
pin_retract = 20  # for 's' key

GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BCM)		#set pin numbering system
GPIO.setup(pin_extend, GPIO.OUT)
pi_pwm_extend = GPIO.PWM(pin_extend, 100)		#create PWM instance with frequency
pi_pwm_extend.start(0)	

GPIO.setup(pin_retract, GPIO.OUT)
pi_pwm_retract = GPIO.PWM(pin_retract, 100)		#create PWM instance with frequency
pi_pwm_retract.start(0)	

try:
    while True:
        
        print("extending")
        pi_pwm_extend.ChangeDutyCycle(100)
        time.sleep(0)
        pi_pwm_extend.ChangeDutyCycle(0)
        time.sleep(1)
        print("retracting")
        pi_pwm_retract.ChangeDutyCycle(100)
        time.sleep(6)
        pi_pwm_retract.ChangeDutyCycle(0)
        time.sleep(1)

        # for i in range(50):
        #     pin_extend.value = 1
        #     time.sleep(0.1)

        # pin_extend.off()

        # for i in range(50):
        #     pin_retract.value = 1
        #     time.sleep(0.1)

        # pin_retract.off()

except KeyboardInterrupt:
    # Clean up GPIO state
    pi_pwm_extend.ChangeDutyCycle(0)
    pi_pwm_retract.ChangeDutyCycle(0)
    print("\nScript terminated by user.")
