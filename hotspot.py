import cv2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

cv2.namedWindow("preview")
#cv2.namedWindow("preview2")

raw_img_path = "/home/remote/FireDetection/rawframes/Sample_Capture_15.tiff"
img_path = "/home/remote/FireDetection/cleanframes/undistorted_Sample_Capture_15.tiff"

raw_frame = cv2.imread(raw_img_path)
frame = cv2.imread(img_path)
undistorted_frame = frame

frame_v = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)[:,:,2]

blurredBrightness = cv2.bilateralFilter(frame_v, 9, 150, 150)
thresh = 50
edges = cv2.Canny(blurredBrightness, thresh, thresh*2, L2gradient=True)

_, mask = cv2.threshold(blurredBrightness, 200, 1, cv2.THRESH_BINARY)
erodeSize = 5
dilateSize = 7
eroded = cv2.erode(mask, np.ones((erodeSize, erodeSize)))
mask = cv2.dilate(eroded, np.ones((dilateSize, dilateSize)))

# Dilation to make the edges thicker
kernel_size = 3  # Adjust the kernel size as needed
dilated_edges = cv2.dilate(edges, np.ones((kernel_size, kernel_size), np.uint8))

_, maskb = cv2.threshold(blurredBrightness, 225, 255, cv2.THRESH_BINARY)

# Find contours in the binary mask

maskb_color = cv2.cvtColor(maskb, cv2.COLOR_GRAY2BGR)

contours, _ = cv2.findContours(maskb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Iterate over contours and draw red dots at their centers
for contour in contours:
    if cv2.contourArea(contour) > 5:  # Set a minimum area threshold to avoid small dots
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(maskb_color, (cX, cY), 2, (0, 0, 255), -1)  # Draw a red dot
            print("X: " + str(cX) + "| Y: " + str(cY))

while True:
    top_row = np.concatenate((raw_frame, undistorted_frame), axis=1)

    # Add labels to the four quadrants

    font_scale = 0.8
    cv2.putText(top_row, "Raw Frame", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
    cv2.putText(top_row, "Dewarped Frame", (raw_frame.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    bottom_row = np.concatenate((cv2.resize(cv2.cvtColor(mask*dilated_edges, cv2.COLOR_GRAY2RGB) | frame, (320, 240), interpolation=cv2.INTER_CUBIC),
                                 cv2.resize(maskb_color, (320, 240), interpolation=cv2.INTER_CUBIC)), axis=1)

    # Add labels to the bottom row
    cv2.putText(bottom_row, "Edge Detection", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,font_scale, (255, 255, 255), 2)
    cv2.putText(bottom_row, "Hot regions", (bottom_row.shape[1] // 2 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    combined_image = np.concatenate((top_row, bottom_row), axis=0)

    cv2.imshow("preview", cv2.resize(combined_image, (1280, 960), interpolation=cv2.INTER_CUBIC))

    key = cv2.waitKey(20)
    if key == 27:
        break