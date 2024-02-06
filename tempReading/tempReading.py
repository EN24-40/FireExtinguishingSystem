import cv2
import numpy as np

# Opening
image_path = '/home/remote/FireDetection/cleanframes/undistorted_Sample_Capture_7.tiff'

image = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)

# Check if the image is read successfully
if image is not None:
   
   # Display the temperature value at the specified (x, y) coordinates
    x = 165
    y = 115
    pixelFrame = image[y,x]
 
    pixelFrame = (pixelFrame / 100) -273.15

    image = cv2.applyColorMap(image,cv2.COLORMAP_INFERNO)

    cv2.circle(image,(x,y), 2, (0,0,0), -1)
    # Convert pixel values to temperature in Celsius
    #temperature = (image - offset) * scale
    cv2.putText(image,"{0:.1f} Celius".format(pixelFrame), (x-80, y-15),cv2.FONT_HERSHEY_PLAIN,1,(255,0,0),2)
 
    #print(f"Temperature at ({x}, {y}): {pixelFrame[x, y]:.2f} Celsius")
    print(pixelFrame)
    # Display the thermal image
    cv2.imshow('Temperature Image', image)
    cv2.waitKey(0)
else:
    print("Error reading the image.")
