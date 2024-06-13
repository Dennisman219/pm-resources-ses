import serial
from time import sleep
import argparse

parser = argparse.ArgumentParser(description="Byte transfer settings",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("byte_length", type=int, help="set byte array length")
args = parser.parse_args()

BYTE_LENGTH = args.byte_length
BAUD_RATE = 115200

TTY_PORT = "/dev/ttyS0"
BYTE_CHUNK_SIZE_BYTES = 1024

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

    # Generate test bytes.
    test_bytes = bytearray([1] * BYTE_LENGTH)

    # Calculate number of chunks and the remaining bytes.
    num_blocks = BYTE_LENGTH // BYTE_CHUNK_SIZE_BYTES
    remainder = BYTE_LENGTH % BYTE_CHUNK_SIZE_BYTES

    # Transmit and receive all of the chunks.
    for i in range(0, num_blocks):
        # Set length in buffer.
        buffer[0] = BYTE_CHUNK_SIZE_BYTES & 0xFF
        buffer[1] = (BYTE_CHUNK_SIZE_BYTES >> 8) & 0xFF

        # Add byte data to buffer.
        buffer.extend(test_bytes[i * BYTE_CHUNK_SIZE_BYTES : (i+1) * BYTE_CHUNK_SIZE_BYTES])

        # Send buffer over serial.
        print("Writing chunk {} of {}...".format(i+1, num_blocks))
        write(buffer)

        # Read bytes over serial.
        read_data.extend(tty.read(BYTE_CHUNK_SIZE_BYTES))

        # Reset buffer.
        buffer = bytearray([0, 0])

    if remainder > 0:
        # Set length in buffer.
        buffer[0] = remainder & 0xFF
        buffer[1] = (remainder >> 8) & 0xFF

        # Add byte data to buffer.
        buffer.extend(test_bytes[num_blocks * BYTE_CHUNK_SIZE_BYTES :])

        # Send buffer over serial.
        print("Writing remaining {} bytes...".format(remainder))
        write(buffer)

        # Read bytes over serial.
        read_data.extend(tty.read(remainder))

    tty.close()

    print("Test bytes sent successfully.")

if __name__ == "__main__":
    main()
