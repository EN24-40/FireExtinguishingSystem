import subprocess
import numpy as np
import cv2  # OpenCV for image handling
from pylepton import Lepton

device = "/dev/spidev0.0"    # Enable SPI interface first and check if camera is at 0.0 or 0.1
with Lepton(device) as l:
    while True:
        _, frame = l.capture()
        # Normalize the captured frame for better visualization
        cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(frame, 8, frame)
        # Convert to BGR format for video
        frame = np.uint8(frame)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
        # Write the frame to stdout
        frame_bytes = frame.tobytes()
      # Change destination IP and port below
        subprocess.call(['ffmpeg', '-i', '-', '-f', 'mpegts', 'udp://<destination IP>:<port>'], stdin=subprocess.PIPE).communicate(input=frame_bytes)
