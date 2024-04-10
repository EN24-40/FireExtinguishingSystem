import math
import sympy as sp

# Senior Design Calculations
# Assumptions
# -Ignore head loss
# -Smooth pipes
v1, v2 = sp.symbols('v1 v2')

# Inputs
rho = 1.940 	# slugs/ft^3
g = 32.2 	# ft/s^2
h_sys = 17.625 	# in
pipe_diamter_inlet = 2.5 	# in
nozzel_diamter = 1.5 		# in

p1 = 10 * 144  	# [lb/ft^2] 
# Given supply pressure, need to verify with fire department what that will be. Assumed 10 psi for now

p2 = 0 * 144  	# [lb/ft^2] outlet atmospheric pressure
friction_losses = 2.2 / 144  # [lb/ft^2] Friction losses in system
y = 40 * 0.3048  	# [m] height of turret

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
E = [sp.Eq(v2, sp.sqrt((2*(p1-p2))/rho + 2*g*(0-Z2) - 2*g*Friction_losses + v1**2)),sp.Eq(v1,(A2*v2)/A1)]

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

R = 60 	# [ft] Input range of turret
# Equation for range of turret to solve for theta
# Equation set equal to zero and starts at -60. Loop finds when REQ=0
REQ = -60
# Note: had to switch the range to be in integers for python
for theta_int in range(-90000, 45000):
	theta_d = theta_int / 1000
	if REQ >= 0:
		break
	else:
	theta_rad = theta_d * math.pi / 180
	REQ = (-1*R) + (v2_sol * math.cos(theta_rad)) / g * (v2_sol * math.sin(theta_rad) + math.sqrt(v2_sol**2 * math.sin(theta_rad)**2 + 2 * g * y))

theta = theta_rad * 180 / math.pi
print(f"Theta: {theta:.3f} degrees)	# Turret angle in degrees, where 0 deg is level.
