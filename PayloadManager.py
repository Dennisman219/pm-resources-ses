import argparse
from time import sleep
import serial
import subprocess
import shlex

from Constants import SerialConfig

def run_command(command) -> bytes:
    command = shlex.split(command)
    result = subprocess.run(command, capture_output=True)

    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        return None
    else:
        return result.stdout

def write_output_string(data: bytes):
    tty = None

    try:
        tty = serial.Serial(SerialConfig.TTY_PORT, SerialConfig.BAUD_RATE, SerialConfig.TIMEOUT)

        sleep(1)

        # Flush buffer.
        tty.flush()

        remaining_bytes = len(data)

        while remaining_bytes > 0:  
            chunk_size = min(SerialConfig.BYTE_CHUNK_SIZE, remaining_bytes)
            tty.write(data[:chunk_size])
            data = data[chunk_size:]
            remaining_bytes -= chunk_size
    
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if tty and tty.is_open:
            tty.close()

def read_input_string(byte_length) -> str:
    read_data = bytearray()
    tty = None
    data_str = None

    try:
        tty = serial.Serial(SerialConfig.TTY_PORT, SerialConfig.BAUD_RATE, SerialConfig.TIMEOUT)

        sleep(1)

        # Flush buffer.
        tty.flush()

        remaining_bytes = byte_length

        while remaining_bytes > 0:
            chunk_size = min(SerialConfig.BYTE_CHUNK_SIZE, remaining_bytes)
            data = tty.read(chunk_size)
            read_data.extend(data)
            remaining_bytes -= len(data)

        data_str = read_data.decode(SerialConfig.ENCODING).strip()

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if tty and tty.is_open:
            tty.close()

    return "" if data_str == None else data_str

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("byte_length", type=int, help="Input byte array length")
    args = parser.parse_args()

    input_string = read_input_string(args.byte_length)

if __name__ == "__main__":
    main()