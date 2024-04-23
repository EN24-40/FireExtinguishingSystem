import numpy as np
import cv2
from matplotlib import pyplot as plt
import os
import sys
sys.path.insert(1, '/home/remote/FireDetection')
import liveHotspot as lh

'''
This sample script takes in the file path to a 16-bit distorted tiff captured from a Lepton 3.1R or 
Lepton UW as the input and creates a LeptonDewarp object which is used to define transformation 
matrices for dewarping a Lepton 3.1R or Lepton UW image. Then, it applies the properties from the
LeptonDewarp object and calls the get_undistorted_img() function to correct the input image. Finally,
the script displays the original distorted image and its corrected version side-by-side. 

The LeptonDewarp class defines how to correct distorted images by setting up the transformation 
matrices and calling the built-in OpenCV functions for the correction.

'''
class LeptonDewarp:
    '''
        Undistorts images captured with Lepton 3.1R(WFOV95) or Lepton UW(WFOV160).
    '''
    
    # Constant nested dictionary that stores the camera matrix, distortion coefficients, and new camera matrix for each WFOV
    camera_parameters = {'WFOV95': { 'camera matrix': [[104.65403680863373, 0.0, 79.12313258957062],
                                                      [0.0, 104.48251047202757, 55.689070170705634],
                                                      [0.0, 0.0, 1.0]],
                                    'distortion coeff': [[-0.39758308581607127,
                                                          0.18068641745671193,
                                                          0.004626461618389028,
                                                          0.004197358204037882,
                                                          -0.03381399499591463]],
                                    'new camera matrix':[[66.54581451416016, 0.0, 81.92717558174809],
                                                             [0.0, 64.58526611328125, 56.23740168870427], 
                                                             [0.0, 0.0, 1.0]]}}
                         
   
    def __init__(self, wfov):
        '''
            LeptonDewarp Constructor that initializes the matrices for dewarping the image
            that corresponds to the field-of-view

            Args:
                wfov = string,
                    field-of-view of the camera, "WFOV95" or "WFOV160"
        '''
        
        self.wfov = wfov

        # Get camera matrix,distortion coefficients, and new camera matrix according to the field of view
        self.camera_matrix = np.array(LeptonDewarp.camera_parameters.get(self.wfov, {}).get('camera matrix'))
        self.distortion_coeff = np.array(LeptonDewarp.camera_parameters.get(self.wfov, {}).get('distortion coeff'))
        self.new_camera_matrix = np.array(LeptonDewarp.camera_parameters.get(self.wfov, {}).get('new camera matrix'))


    def get_undistorted_img(self, img, retain_pixels=False, crop=False):
        '''
            Undistort the image

            Args:
                img = numpy array,
                    distorted image in uint8

                cretain_pixels = boolean,
                    default to False, dewarp image to have a fixed IFOV
                    True will keep all black border pixels after dewarped
                
                crop = boolean,
                    only applies when retain_pixels is True;
                    crops image to remove black pixels
            
            Output:
                undistorted_img = numpy array,
                    corrected image;
                    same resolution as input if crop isn't applied
        '''

        if self.wfov == 'WFOV95':
            # Apply matrices to undistort function to correct image
            if retain_pixels:
                # Keep all pixels from input after dewarp
                undistorted_img = cv2.undistort(img, self.camera_matrix,
                                                self.distortion_coeff,
                                                None,
                                                self.new_camera_matrix)

                if crop:
                    # Get image dimension
                    img_dim = undistorted_img.shape
                    row = img_dim[0]
                    col = img_dim[1]

                    # OpenCV generated cropping matrix still retains a few black pixels,
                    # return the corrected image with those pixels cropped out
                    undistorted_img = undistorted_img[14:row-18, 12:col-12]
            else:
                # Remove borders after dewarp
                undistorted_img = cv2.undistort(img,
                                                self.camera_matrix,
                                                self.distortion_coeff)


        return undistorted_img

def convert_raw_img(img_in):
    '''
        Normalizes and converts a uint16 raw image captured from a Lepton into uint8

        Args: 
            img_in = numpy array

        Output: 
            img = numpy array,
                  image in uint8
    '''

    img = cv2.normalize(img_in, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
    img = (img/256).astype('uint8')
    
    return img

# Sample Code applying the LeptonDewarp Class
if __name__ == "__main__":

    # Define file path and file name to distorted image and read it
    input_folder = '/home/remote/FireDetection/rawframes'
    output_folder = '/home/remote/FireDetection/cleanframes'
    filename = 'Live_Capture.tiff'
    webapp_filename = 'Live_Capture.jpg'

    input_file_path = os.path.join(input_folder, filename)

# Check if the path is a file (not a directory)
if os.path.isfile(input_file_path):
    # Read the input image
    img = cv2.imread(input_file_path, -1)

    # Resize image
    dim = (160, 120)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # Create an object to get the matrices that correspond to the fov
    cam = LeptonDewarp("WFOV95")

    # Apply distortion correction on the input image
    undistorted_img = cam.get_undistorted_img(img, True)

    new_dim = (320, 240)

    undistorted_img = cv2.resize(undistorted_img, new_dim, interpolation=cv2.INTER_AREA)

    # Save the undistorted image to the output folder
    output_file_path = os.path.join(output_folder, f"undistorted_{filename}")
    cv2.imwrite(output_file_path, undistorted_img)
    webapp_output_file_path = os.path.join("/var/www/html", f"undistorted_{webapp_filename}")
    cv2.imwrite(webapp_output_file_path, undistorted_img)
    # os.system("python3 /home/remote/FireDetection/liveHotspot.py &")
    lh.liveHotspot()
    exit()

    # Display original and corrected images side by side
    # fig = plt.figure()
    # orig = fig.add_subplot(1, 2, 1)
    # orig.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # orig.set_title("original")
    # plt.axis('off')
    # result = fig.add_subplot(1, 2, 2)
    # result.imshow(cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2RGB))
    # result.set_title("undistorted")
    # plt.axis('off')
    #plt.show()
exit()
