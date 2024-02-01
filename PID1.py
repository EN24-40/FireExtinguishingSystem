def main():
    # Set up and configure GPIO pins:
    from gpiozero import PWMLED
    import keyboard
    import time
    pin_w = PWMLED(21)  # 'w' key
    pin_s = PWMLED(20)  # 's' key


    # Declare global variables:
    time = 0
    integral = 0
    time_prev = -1e-6
    e_prev = 0

    # Prompt user to enter parameters
    param()

    # Control actuators:
    actuators()

    # Reset Parameters:
    reset()

    # Clean up GPIO state:
    pin_w.off()
    pin_s.off()
    print("\nScript terminated by user.")    


# Function for entering parameters:
def param():
    Kp = input('Enter Kp: ')
    Ki = input('Enter Ki: ')
    Kd = input('Enter Kd: ')
    setpoint = input('Enter Desired Output (setpoint): ')


# Function to calculate value of manipulated variable:
def PID(Kp, Ki, Kd, setpoint, measurement):
    global time, integral, time_prev, e_prev

    ### Value of offset - when the error is equal zero
    offset = 320
    
    # PID calculations
    e = setpoint - measurement
        
    P = Kp*e
    integral = integral + Ki*e*(time - time_prev)
    D = Kd*(e - e_prev)/(time - time_prev)

    # calculate manipulated variable - MV 
    MV = offset + P + integral + D
    
    # update stored data for next iteration
    e_prev = e
    time_prev = time
    return MV


# Function controlling the actuators:
def actuators():
    # number of steps:
    n = 250

    deltat = 0.1
    time_prev = 0

    ### Initial actuator displacement
    y0 = pin_w.value

    # Initialize vectors for monitoring control performance
    y_sol = [y0]
    t_sol = [time_prev]


    for i in range(1, n):
        time = i * deltat

         = PID(Kp, Ki, Kd, setpoint, y_sol[-1])

        time_sol.append(time)
        time_prev = time


# Function to reset parameters:
def reset():
    Kp = 0
    Ki = 0
    Kd = 0
    setpoint = 0
    

# Call the main function:
main()
