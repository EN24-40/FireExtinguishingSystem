import numpy as np
import cv2
import os


#image_src = cv2.imread('')

# Points in source (real world coordinates)
# Bret under hoop, back corner of house, Connor near garage, Connor bottom right corner
pts_src = np.array([[-15.666, 1,1], [-15.666, 40,1], [5, 23,1], [1, 15, 1]]) # in FT (N+, S-, E+, W-)

# Points in camera image (pixels)
pts_dst = np.array([[-126, 65,1], [-59, 154, 1], [14, 131, 1], [140, 60, 1]])  # in Pixels

# Calculate H in homography equation
h, status = cv2.findHomography(pts_src, pts_dst)

inv_h = np.linalg.inv(h)

spot = np.array([[0],
                [154], 
                [1]])

prod = np.dot(inv_h, spot)

val = 1 /prod[2]   

final = np.multiply(val, prod)

#print(inv_h.size())
print(h)
print('\n')
print('\n')
print(final)
