import smbus
import time
from Constants import DiceConfig

class DicePayload:
    """
    Interface for controlling the Dice Payload via I2C.
    Implements commands as specified in the ICD.
    """
    
    def __init__(self, bus_num=1, address=None):
        """
        Initialize the Dice Payload controller.
        
        Args:
            bus_num: I2C bus number (default: 1)
            address: I2C slave address (default: from Constants.py)
        """
        self.bus = smbus.SMBus(bus_num)
        self.address = address if address is not None else DiceConfig.ADDRESS
        
    def _send_command(self, command, data=None):
        """
        Send a command to the Dice Payload controller.
        
        Args:
            command: Command byte
            data: Optional data byte to send with the command
        
        Returns:
            None
        """
        if data is not None:
            self.bus.write_i2c_block_data(self.address, command, [data])
        else:
            self.bus.write_byte(self.address, command)
    
    def _read_byte(self, command):
        """
        Read a byte from the Dice Payload controller.
        Reads the 4-byte response packet and returns the data byte.
        
        Args:
            command: Command byte
        
        Returns:
            byte: The data byte from the response packet
        """
        self.bus.write_byte(self.address, command)
        
        # Read the 4-byte response packet: Start, Command ID, Data, Stop
        response = []
        for i in range(4):
            response.append(self.bus.read_byte(self.address))
        
        # Parse packet format
        start_byte = response[0]  # Should be '$' (0x24)
        command_id = response[1]  # Should match the command sent
        data_byte = response[2]   # The actual data
        stop_byte = response[3]   # Should be '\n' (0x0A)
        
        # Validate packet format
        if start_byte != 0x24 or stop_byte != 0x0A:  # '$' and '\n'
            print("communication error")
            #return 0  # Return default value on error
        
        return data_byte
    
    def get_status(self):
        """
        Read the status byte from the response packet.
        
        Returns:
            int: Status data byte
        """
        return self._read_byte(DiceConfig.CMD_STATUS)
    
    def wait_until_ready(self, timeout=10):
        """
        Wait until the payload is no longer in a running state.
        
        Args:
            timeout: Maximum time to wait in seconds
        
        Returns:
            bool: True if payload is ready, False if timeout occurred
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status()
            if status == DiceConfig.STATUS_OK or status == DiceConfig.STATUS_INIT or status == DiceConfig.STATUS_FAIL:
                return True
            time.sleep(0.1)
        return False
    
    # Read commands
    def read_motor1_speed(self):
        """Read motor 1 speed (PWM value)"""
        return self._read_byte(DiceConfig.CMD_R_M1_SPEED)
    
    def read_motor2_speed(self):
        """Read motor 2 speed (PWM value)"""
        return self._read_byte(DiceConfig.CMD_R_M2_SPEED)
    
    def read_motor1_length(self):
        """Read motor 1 length (in 100ms units)"""
        return self._read_byte(DiceConfig.CMD_R_M1_LENGTH)
    
    def read_motor2_length(self):
        """Read motor 2 length (in 100ms units)"""
        return self._read_byte(DiceConfig.CMD_R_M2_LENGTH)
    
    def read_motor1_position(self):
        """
        Read motor 1 position.
        
        Returns:
            int: 0x00 (unknown), 0x01 (clamped), 0x02 (unclamped)
        """
        return self._read_byte(DiceConfig.CMD_R_M1_POSITION)
    
    def read_led_brightness(self):
        """Read LED brightness (PWM value)"""
        return self._read_byte(DiceConfig.CMD_R_LED_BRIGHTNESS)
    
    def read_led_status(self):
        """Read LED status"""
        return self._read_byte(DiceConfig.CMD_R_LED_STATUS)
    
    # Write commands
    def write_motor1_speed(self, speed):
        """
        Set motor 1 speed (PWM value).
        
        Args:
            speed: PWM value (0-255)
        """
        self._send_command(DiceConfig.CMD_W_M1_SPEED, speed)
    
    def write_motor2_speed(self, speed):
        """
        Set motor 2 speed (PWM value).
        
        Args:
            speed: PWM value (0-255)
        """
        self._send_command(DiceConfig.CMD_W_M2_SPEED, speed)
    
    def write_motor1_length(self, length):
        """
        Set motor 1 length (in 100ms units).
        
        Args:
            length: Length in 100ms units
        """
        self._send_command(DiceConfig.CMD_W_M1_LENGTH, length)
    
    def write_motor2_length(self, length):
        """
        Set motor 2 length (in 100ms units).
        
        Args:
            length: Length in 100ms units
        """
        self._send_command(DiceConfig.CMD_W_M2_LENGTH, length)
    
    def write_led_brightness(self, brightness):
        """
        Set LED brightness (PWM value).
        
        Args:
            brightness: PWM value (0-255)
        """
        self._send_command(DiceConfig.CMD_W_LED_BRIGHTNESS, brightness)
    
    # LED control
    def led_on(self):
        """Turn LED on"""
        self._send_command(DiceConfig.CMD_LED_ON)
    
    def led_off(self):
        """Turn LED off"""
        self._send_command(DiceConfig.CMD_LED_OFF)
    
    # Motor action commands
    def clamp(self):
        """Execute clamp dice routine (non-blocking)"""
        self._send_command(DiceConfig.CMD_CLAMP)
    
    def clamp_sync(self):
        """Execute clamp dice routine and wait until ready"""
        self._send_command(DiceConfig.CMD_CLAMP)
        return self.wait_until_ready()
    
    def unclamp(self):
        """Execute unclamp dice routine (non-blocking)"""
        self._send_command(DiceConfig.CMD_UNCLAMP)
    
    def unclamp_sync(self):
        """Execute unclamp dice routine and wait until ready"""
        self._send_command(DiceConfig.CMD_UNCLAMP)
        return self.wait_until_ready()
    
    def stop_motors(self):
        """Stop all motors"""
        self._send_command(DiceConfig.CMD_STOP_M1_M2)
    
    def run_motor1_clockwise(self):
        """Run motor 1 clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CW)
    
    def run_motor1_counter_clockwise(self):
        """Run motor 1 counter-clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CCW)
    
    def run_motor2_clockwise(self):
        """Run motor 2 clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M2_CW)
    
    def run_motor2_counter_clockwise(self):
        """Run motor 2 counter-clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M2_CCW)
    
    def run_motor1_cw_motor2_cw(self):
        """Run motor 1 and motor 2 clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CW_M2_CW)
    
    def run_motor1_ccw_motor2_cw(self):
        """Run motor 1 counter-clockwise and motor 2 clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CCW_M2_CW)
    
    def run_motor1_cw_motor2_ccw(self):
        """Run motor 1 clockwise and motor 2 counter-clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CW_M2_CCW)
    
    def run_motor1_ccw_motor2_ccw(self):
        """Run motor 1 and motor 2 counter-clockwise"""
        self._send_command(DiceConfig.CMD_RUN_M1_CCW_M2_CCW)
    
    # Switch control
    def disable_all_switches(self):
        """Disable all switches"""
        self._send_command(DiceConfig.CMD_W_DISABLE_SWITCH_ALL)
    
    def enable_all_switches(self):
        """Enable all switches"""
        self._send_command(DiceConfig.CMD_W_ENABLE_SWITCH_ALL)
    
    def configure_switches(self, clamped1=True, clamped2=True, unclamped1=True, unclamped2=True):
        """
        Configure switches individually.
        
        Args:
            clamped1: Enable/disable clamped1 switch
            clamped2: Enable/disable clamped2 switch
            unclamped1: Enable/disable unclamped1 switch
            unclamped2: Enable/disable unclamped2 switch
        """
        # Construct command byte: 1110xxxx where x are the switch settings
        cmd = 0xE0
        if clamped1:
            cmd |= 0x01
        if clamped2:
            cmd |= 0x02
        if unclamped1:
            cmd |= 0x04
        if unclamped2:
            cmd |= 0x08
        
        self._send_command(cmd)

    def reset(self):
        """Reset system variables"""
        self._send_command(DiceConfig.CMD_RESET)

    def dice_sequence(self):
        self.unclamp_sync()
        status = self.get_status()
        self.clamp_sync()
        status = self.get_status()
        