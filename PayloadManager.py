import argparse
from time import sleep
import serial
from Constants import SerialConfig

def read_input_string(byte_length):
    read_data = bytearray()
    tty = None

    try:
        tty = serial.Serial(SerialConfig.TTY_PORT, SerialConfig.BAUD_RATE, SerialConfig.TIMEOUT)

        sleep(1)

        # Flush buffer.
        tty.flush()

        remaining_bytes = byte_length

        while remaining_bytes > 0:
            chunk_size = min(SerialConfig.BYTE_CHUNK_SIZE, remaining_bytes)
            data = serial.read(chunk_size)
            read_data.extend(data)
            remaining_bytes -= len(data)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if tty and tty.is_open:
            tty.close()

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("byte_length", type=int, help="Input byte array length")
    args = parser.parse_args()

    read_input_string(args.byte_length)

if __name__ == "__main__":
    main()