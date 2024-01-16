import serial
from PIL import Image
from time import sleep
import os
import math
import argparse

parser = argparse.ArgumentParser(description="Image transfer settings",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filepath", help="set image path")
args = parser.parse_args()

IMAGE_FILE_PATH = args.filepath
BAUD_RATE = 1152000
IMAGE_MODE = "RGB"

TTY_PORT = "/dev/ttyS0"
IMAGE_CHUNK_SIZE_BYTES = 1024

# Open serial port.
tty = serial.Serial(TTY_PORT, BAUD_RATE, timeout=256)

# Write to serial port.
def write(data: bytes):
    tty.write(data)

def main():
    read_data = bytearray()
    buffer = bytearray([0, 0])

    # Open serial port.
    tty.close()
    tty.open()

    # Necessary sleep, open doesn't immediately open.
    sleep(1)

    # Flush buffer so we can receive new stuff.
    tty.flush()

    # Open image file as bytes.
    fptr = open(IMAGE_FILE_PATH, "rb")

    # Get image size.
    image_size = os.path.getsize(IMAGE_FILE_PATH)
    print("Image size: " + str(image_size))

    # Calculate number of chunks and the remaining bytes.
    num_blocks = image_size // IMAGE_CHUNK_SIZE_BYTES
    remainder = image_size % IMAGE_CHUNK_SIZE_BYTES

    # Transmit and receive all of the chunks.
    for i in range(0, num_blocks):
        # Set length in buffer.
        buffer[0] = IMAGE_CHUNK_SIZE_BYTES & 0xFF
        buffer[1] = (IMAGE_CHUNK_SIZE_BYTES >> 8) & 0xFF

        # Add image data to buffer.
        buffer.extend(fptr.read(IMAGE_CHUNK_SIZE_BYTES))

        # Send buffer over serial.
        print("Writing chunk {} of {}...".format(i+1, num_blocks))
        write(buffer)

        # Read image over serial.
        read_data.extend(tty.read(IMAGE_CHUNK_SIZE_BYTES))

        # Reset buffer.
        buffer = bytearray([0, 0])

    if remainder > 0:
        # Set length in buffer.
        buffer[0] = remainder & 0xFF
        buffer[1] = (remainder >> 8) & 0xFF

        # Add image data to buffer.
        buffer.extend(fptr.read(remainder))

        # Send buffer over serial.
        print("Writing remaining {} bytes...".format(remainder))
        write(buffer)

        # Read image over serial.
        read_data.extend(tty.read(remainder))

    tty.close()
    fptr.close()

    # Calculate width and height.
    width = 0
    height = 0

    if IMAGE_MODE == "RGB":
        width = int(math.sqrt(image_size // 3))
    elif IMAGE_MODE == "RGBA":
        width = int(math.sqrt(image_size // 4))
    else:
        width = int(math.sqrt(image_size))

    height = width

    print("Width: {}, Height: {}".format(width, height))

    # Save image.
    img = Image.frombytes(IMAGE_MODE, (width, height), bytes(read_data))
    img.save("/home/webcam/images/msp/received.png")

if __name__ == "__main__":
    main()