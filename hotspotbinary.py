import cv2
import numpy as np

cv2.namedWindow("preview")

img_path = "/home/remote/FireDetection/cleanframes/undistorted_Sample_Capture_15.tiff"
frame = cv2.imread(img_path)

# Convert the image to RGB color space
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

frame_v = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)[:,:,2]

blurredBrightness = cv2.bilateralFilter(frame_v, 9, 150, 150)
thresh = 5
edges = cv2.Canny(blurredBrightness, thresh, thresh*2, L2gradient=True)

_, mask = cv2.threshold(blurredBrightness, 200, 255, cv2.THRESH_BINARY)  # Note the change in threshold value

while True:
    cv2.imshow("preview", cv2.resize(mask, (640, 480), interpolation=cv2.INTER_CUBIC))

    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
