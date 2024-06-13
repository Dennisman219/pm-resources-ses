import serial
from time import sleep
import argparse

parser = argparse.ArgumentParser(description="Byte receive settings",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("byte_length", type=int, help="set byte array length")
args = parser.parse_args()

BYTE_LENGTH = args.byte_length
BAUD_RATE = 115200
TTY_PORT = "/dev/tty.usbmodem000000031"
BYTE_CHUNK_SIZE_BYTES = 1024

def main():
    read_data = bytearray()
    tty = None

    try:
        tty = serial.Serial(TTY_PORT, BAUD_RATE, timeout=256)
        # Necessary sleep, open doesn't immediately open.
        sleep(1)

        # Flush buffer so we can receive new stuff.
        tty.flush()

        # Calculate number of chunks and the remaining bytes.
        num_blocks = BYTE_LENGTH // BYTE_CHUNK_SIZE_BYTES
        remainder = BYTE_LENGTH % BYTE_CHUNK_SIZE_BYTES

        # Receive all of the chunks.
        for i in range(0, num_blocks):
            # Read bytes from serial.
            print("Reading chunk {} of {}...".format(i + 1, num_blocks))
            buffer = tty.read(BYTE_CHUNK_SIZE_BYTES)
            read_data.extend(buffer)

        if remainder > 0:
            # Read remaining bytes from serial.
            print("Reading remaining {} bytes...".format(remainder))
            buffer = tty.read(remainder)
            read_data.extend(buffer)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if tty and tty.is_open:
            tty.close()

    # Print received bytes.
    print("Received bytes:", read_data)

if __name__ == "__main__":
    main()
