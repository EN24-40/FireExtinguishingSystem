import cv2
import numpy as np

# Opening
image_path = '/home/remote/FireDetection/cleanframes/undistorted_Sample_Capture_16.tiff'

image = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)

# Check if the image is read successfully
if image is not None:
   

    # Assuming calibration parameters (you need to use your own values)
    offset = 263
    scale = 0.01



    # Convert pixel values to temperature in Celsius
    temperature = (image - offset) * scale

    # Display the temperature value at the specified (x, y) coordinates
    x = 165
    y = 115
    print(f"Temperature at ({x}, {y}): {temperature[x, y]:.2f} Celsius")

    # Display the thermal image
    cv2.imshow('Temperature Image', image)
    cv2.waitKey(0)
else:
    print("Error reading the image.")
