import cv2
import numpy as np

# Opening
image_path = '/home/remote/FireDetection/cleanframes/undistored_Sample_Capture_3.tiff'
image = cv2.imread(image_path, cv2.IMREAD_ANYDEPTH)


array = np.array(image)

#print(array.shape)
#(240, 320) is the shape
#i think its supposed to be 160x120
#print(array.dtype)
#the array type 8 bits
#to look at the values being read, saves a csv in current dir.
np.savetxt("dataTemp.csv", array, delimiter = ",")

# Check if the image is read successfully
if image is not None:
   
    # Display the temperature value at the specified (x, y) coordinates
    x = 165
    y = 115
    pixelFrame = image[y,x]
    # Convert pixel values to temperature in Celsius, idk if the values are correct
    pixelFrame = (pixelFrame / 100) -273.15
    #adds color to the photo
    image = cv2.applyColorMap(image,cv2.COLORMAP_INFERNO)
    #adds a small circle in where the temperature is measured
    cv2.circle(image,(x,y), 2, (0,0,0), -1)
    
    #adds the temperature reading near the circle
    cv2.putText(image,"{0:.1f} Celius".format(pixelFrame), (x-80, y-15),cv2.FONT_HERSHEY_PLAIN,1,(255,0,0),2)
 
    #prints the the temp val
    print(pixelFrame)
    # Display the thermal image
    cv2.imshow('Temperature Image', image)
    #exits if there is any key pressed
    cv2.waitKey(0)
#unsuccessful
else:
    print("Error reading the image.")
