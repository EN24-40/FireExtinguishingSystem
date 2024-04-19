import cv2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def liveHotspot():

    img_path = "/home/remote/FireDetection/cleanframes/undistorted_Live_Capture.tiff"
    frame = cv2.imread(img_path)

    # Convert image to HSV color space
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for red color in HSV
    lower_red = np.array([0, 100, 100])  # Lower bound for red in HSV
    upper_red = np.array([10, 255, 255])  # Upper bound for red in HSV

    # Create a mask for the red regions
    mask_red = cv2.inRange(frame_hsv, lower_red, upper_red)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over contours and draw red dots at their centers
    for contour in contours:
        if cv2.contourArea(contour) > 5:  # Set a minimum area threshold to avoid small dots
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cX, cY), 2, (0, 0, 255), -1)  # Draw a red dot
                print("FireDetected")
                print("X: " + str(cX) + "| Y: " + str(cY))

    # Display the result
    # cv2.imshow("Red Areas", frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# Call the function to run
#liveHotspot()
