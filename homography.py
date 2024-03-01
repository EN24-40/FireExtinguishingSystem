import numpy as np
import cv2
import os


#image_src = cv2.imread('')

# Points in source (real world coordinates)
# Bret under hoop, back corner of house, Connor near garage, Connor bottom right corner
pts_src = np.array([[0, -15.666,1], [40, -15.666,1], [23, 5,1], [15, 0, 1]]) # in FT (N+, S-, E+, W-)

# Points in camera image (pixels)
pts_dst = np.array([[34, 175, 1], [101, 88, 1], [174, 109,1], [300, 180, 1]])  # in Pixels

# Calculate H in homography equation
h, status = cv2.findHomography(pts_src, pts_dst)

inv_h = np.linalg.inv(h)

spot = np.array([[140],
                [86], 
                [1]])

prod = np.dot(inv_h, spot)

val = 1 /prod[2]   

final = np.multiply(val, prod)

#print(inv_h.size())
print(h)
print('\n')
print('\n')
print(final)
