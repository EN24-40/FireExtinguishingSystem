# Fire Extinguishing System: Detection and Control

This software was completed by EN24-40 at Gonzaga University. The goal was to create an automated fire extinguishing turret that is able to autonomously detect fires and move the turret to the correct angles to extinguish the fire. For the project, a FLIR Lepton 3.1r thermal camera was used to detect hotspots. The control system is designed for two electronic linear actuators on the turret constructed by EN24-50.

## Important Files
There are a few files that are most important in the use of the system

### Thermal Camera

For the thermal camera, `LeptonModule/software/raspberrypi_video` contains a modified version of the software provided in `https://github.com/groupgets/LeptonModule`. This program is in charge of everything to do with the thermal camera. There are 3 especially important files
1. `main.cpp`: Controls the overall flow of the program including starting the rest of the automation software.
2. `LeptonModule.cpp`: Controls the functionality of the thermal camera.
3. `dewarp/liveDewarp.py`: Runs the correction algorithm to remove the fisheye frome the wide angle lense.

### Localization

Once a fire has been detected, the system must determine where in the real world that pixel corresponds to. This is a process known as localization and is done using a processs known as homography
1. `homography.py`: Controls this algorithm, when setting up the thermal camera, pts_src and pts_dst must be set as calibration points. `https://learnopencv.com/homography-examples-using-opencv-python-c/` has more information about how this was implemented.

### Control

There are a few different ways that the turret can be controled.
1. `pygametest.py`: Allows the system to be controlled with a PlayStation 4 controller. As long as the controller is connected over bluetooth, the program will be able to recognize it. Has not been tested with other controllers.
2. `angleTest.py`: Allows the user to input 2 angles, one for pitch and yaw, and the turret will move to those points, pitch is set to 0 degrees as straight forward with positive being aiming up, etc. Yaw is set with 0 being straight forward and postive angles being right.
3. `fullControlTest.py`: This is the fully autonomous mode, the program will take it the location of the fire in feet forwards and feel left(-) or right(+), then will do the calculations to determine which angles the turrent should be at to aim at the fire.
