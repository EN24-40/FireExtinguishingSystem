import numpy as np
import cv2
#importing the hotspot variables 
# from hotspot import cX
# from hotspot import cY

def homography(cX, cY):
    # Points in source (real world coordinates)
    # Bret under hoop, back corner of house, Connor near garage, Connor bottom right corner
    pts_src = np.array([[-7.083, 7.916,1], [0, 16,1], [-7.916, 16,1], [9.166, 16, 1],[0,12.417,1]]) # in FT 

    # Points in camera image (pixels)
    pts_dst = np.array([[-62,49,1], [5, 101, 1], [-44, 102, 1], [63, 106, 1],[3,86,1]])  # in Pixels

    # Calculate H in homography equation
    h, status = cv2.findHomography(pts_src, pts_dst)

    #inversing so we can get real world coordinates
    inv_h = np.linalg.inv(h)




    #a loop for testing many spots if wanted.
    multiple_value_testing = False

    if multiple_value_testing == True:

        # These are the min and max "x" and "y" (IN PIXELS) to get real world coords from
        x_max_val = 160      #changable max value to iterate through
        x_min_val = -160
        x_step = 10    #value to iterate by, sapce between coords

        y_max_val = 260
        y_min_val = 0
        y_step = 1    #value to iterate by, sapce between coords

        # Some pretty printing stuff, ignore.
        print("X Pix\t Y Pix\t X Real (ft)\t\t Y Real (ft)")
        print("-----------------------------------------------------------------")

        # Double loop, takes an x value, goes through all y values for that x, then goes to next x
        for x in list(range(x_min_val, x_max_val + 1, x_step)):
            for y in list(range(y_min_val, y_max_val + 1, y_step)):

                # Pixel location to get real world coords for
                spot = np.array([[x],
                                [y],
                                [1]])

                # Dot product h matrix with pixel matrix
                prod = np.dot(inv_h, spot)

                # Reciprocal of z value, used to multiply matrix to get answer
                val = 1 / prod[2]

                # Multiply matrix by reciprocal to make z = 1 and therefore other vals (x, y) are in real world coord (ft)
                final = np.multiply(val, prod)

                # If Y Pixel is less than 60 (it seems), the y value in feet is negative, which is not possible
                # so it is actually just the minimum value of y = 1.
                # if final[1] < 0:
                #     final[1] = 1
                
                # Loop print values: X pixel, Y Pixel, X Real Coord, Y Real Coord
                print(x, "\t", y, "\t", final[0][0], "\t", final[1][0])



    else:   # In the case of else, a single point can be input and used. Automation uses this.

        #putting the hotspot in an array
        spot = np.array([[cX-160],
                        [240-cY], 
                        [1]])
        # spot = np.array([[105],
        #                  [49], 
        #                  [1]])

        prod = np.dot(inv_h, spot)

        #val is the reciprocal of the z axis number
        val = 1 /prod[2]   
        #multiplying so z is 1
        final = np.multiply(val, prod)

        # If real Y value is negative (pixel below 60 input for Y), then Y is actually = 1
        if final[1] < 0:
            final[1] = 1

        #print(inv_h.size())
        # print(h)
        # print('\n')
        # print('\n')


        print(final[0][0], "\t", final[1][0])

    return