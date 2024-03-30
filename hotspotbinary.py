import cv2
import numpy as np

cv2.namedWindow("preview")

img_path = "/home/remote/FireDetection/cleanframes/undistorted_Sample_Capture_15.tiff"
frame = cv2.imread(img_path)

# Convert the image to RGB color space
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

frame_v = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)[:, :, 2]

blurredBrightness = cv2.bilateralFilter(frame_v, 9, 150, 150)

_, mask = cv2.threshold(blurredBrightness, 200, 255, cv2.THRESH_BINARY)

# Find contours in the mask
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw contours on the original image
for contour in contours:
    # You can change the color and thickness of the contour lines here
    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)  # Drawing green lines

while True:
    # Resize for display
    display_frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_CUBIC)
    cv2.imshow("preview", display_frame)

    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break

cv2.destroyAllWindows()
