import cv2
import numpy as np
import spidev
import time

def capture_frame(spi):
    # Send command to start frame capture
    spi.xfer2([0x00, 0x00, 0x01, 0x00])

    # Wait for a brief moment to allow frame capture
    time.sleep(0.1)

    # Read frame data in chunks
    chunk_size = 4096  # Adjust the chunk size as needed
    num_chunks = (80 * 60 + 4) // chunk_size

    response = []
    for _ in range(num_chunks):
        chunk = spi.xfer2([0x00] * chunk_size)
        response.extend(chunk)

    # Extract frame data
    frame_size = 60 * 80 * 2  # Size of a 60x80 frame with 2 bytes per pixel
    frame_data = np.array(response[4:4 + frame_size])

    # Check if the received data size matches the expected frame size
    if len(frame_data) != frame_size:
        print("Error: Received data size does not match the expected frame size.")
        return None

    # Reshape the frame data into a 2D array
    frame = frame_data.reshape((60, 80))

    return frame

def save_frame_as_image(frame, output_path='captured_frame.jpg'):
    if frame is None:
        print("Error: Cannot save NoneType frame.")
        return

    # Check for NaN or infinite values in the frame
    if np.isnan(frame).any() or np.isinf(frame).any():
        print("Error: Frame contains NaN or infinite values, cannot save.")
        return

    # Check for valid min and max values
    min_value, max_value = np.nanmin(frame), np.nanmax(frame)
    if min_value == max_value:
        print("Error: Frame has constant values, cannot normalize.")
        return

    # Normalize the frame data to the 0-255 range for saving as an image
    normalized_frame = ((frame - min_value) / (max_value - min_value) * 255).astype(np.uint8)

    # Save the frame as an image
    cv2.imwrite(output_path, normalized_frame)

    print("Frame captured and saved as 'captured_frame.jpg'")

if __name__ == "__main__":
    # Open SPI connection (you might need to adjust the bus and device)
    spi = spidev.SpiDev()
    spi.open(0, 1)  # bus 0, device 1 (you might need to adjust)

    try:
        # Capture a frame
        frame = capture_frame(spi)

        # Save the frame as an image
        save_frame_as_image(frame)

        print("Frame captured and saved as 'captured_frame.jpg'")
    finally:
        # Close SPI connection
        spi.close()
