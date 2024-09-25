from adafruit_bus_device import i2c_device
from adafruit_register import i2c_bit
from adafruit_register import i2c_bits
# from typing import Union, List, Tuple, Optional
from busio import I2C
import time

AS1115_REGISTER = {
	'DECODE_MODE'		: 0x09,  # Sets the decode mode (BCD or HEX).
	'GLOBAL_INTENSITY'	: 0x0A,  # Sets the entire display intensity.
	'SCAN_LIMIT'		: 0x0B,  # Controls how many digits are to be displayed.
	'SHUTDOWN'			: 0x0C,  #
	'SELF_ADDRESSING'	: 0x2D,  # Uses 2 of the 16 keys to change the device's address.
	'FEATURE'			: 0x0E,  # Enables various features such as clock mode and blinking.
	'DISPLAY_TEST_MODE'	: 0x0F,  # Detects open or shorted LEDs.
	'DIG01_INTENSITY'	: 0x10,  # Sets the display intensity for digit 0 and 1.
	'DIG23_INTENSITY'	: 0x11,  # Sets the display intensity for digit 2 and 3.
	'DIG45_INTENSITY'	: 0x12,  # Sets the display intensity for digit 4 and 5.
	'DIG67_INTENSITY'	: 0x13,  # Sets the display intensity for digit 6 and 7.
	'KEY_A'				: 0x1C,  # Gets the result of the debounced keyscan for KEYA.
	'KEY_B'				: 0x1D	 # Gets the result of the debounced keyscan for KEYB.
}

AS1115_LED_DIAG_REG = {
    'DIAG_DIGIT0'		: 0x14,  # Gets the results of the LEDS open/short test for digit 0.
	'DIAG_DIGIT1'		: 0x15,  # Gets the results of the LEDS open/short test for digit 1.
	'DIAG_DIGIT2'		: 0x16,  # Gets the results of the LEDS open/short test for digit 2.
	'DIAG_DIGIT3'		: 0x17,  # Gets the results of the LEDS open/short test for digit 3.
	'DIAG_DIGIT4'		: 0x18,  # Gets the results of the LEDS open/short test for digit 4.
	'DIAG_DIGIT5'		: 0x19,  # Gets the results of the LEDS open/short test for digit 5.
	'DIAG_DIGIT6'		: 0x1A,  # Gets the results of the LEDS open/short test for digit 6.
	'DIAG_DIGIT7'		: 0x1B,  # Gets the results of the LEDS open/short test for digit 7.
}

LED_DIGIT = {
    'G': 0,
    'F': 1,
    'E': 2,
    'D': 3,
    'C': 4,
    'B': 5,
    'A': 6,
    'DP': 7
}

AS1115_SHUTDOWN_MODE = {
	'SHUTDOWN_MODE'	    : 0x00,  #  Shutdown and reset FEATURE register to default settings.
	'NORMAL_OPERATION'  : 0x01,  #  Resume operation and reset FEATURE register to default settings.
	'RESET_FEATURE'	    : 0x00,  #  FEATURE register is resetted to default settings.
	'PRESERVE_FEATURE'  : 0x80,  #  FEATURE register is unchanged.
}

AS1115_DECODE_SEL ={
	'CODE_B_DECODING'	: 0x00,
	'HEX_DECODING'	    : 0x01,
}

AS1115_FEATURE = {
	'CLOCK_ACTIVE'	    : 0,  #  Enables the external clock.
	'RESET_ALL'		    : 1,  #  Resets all control register except the FEATURE register.
	'DECODE_SEL'	    : 2,  #  Enable Code-B or HEX decoding for the selected digits.
	'BLINK_ENABLE'	    : 4,  #  Enables blinking.
	'BLINK_FREQ_SEL'	: 5,  #  Sets the blinking frequency.
	'SYNC'			    : 6,  #  Synchronize blinking with LD/CS pin.
	'BLINK_START'		: 7,  #  Sets whether to start the blinking with the display turned on or off.
}

AS1115_DISPLAY_TEST_MODE = {
	'DISP_TEST':    0,  #  Optical display test.
	'LED_SHORT':    1,  #  Starts a test for shorted LEDs.
	'LED_OPEN':     2,  #  Starts a test for open LEDs.
	'LED_TEST':     3,  #  Indicates an ongoing open/short LED test.
	'LED_GLOBAL':   4,  #  Indicates that the last open/short LED test has detected an error.
	'RSET_OPEN':    5,  #  Checks if external resistor Rset is open.
	'RSET_SHORT':   6,  #  Checks if external resistor Rset is shorted.
}

# AS1115_DOT = 0x80
# LETTERS = {
#     'A': 0x77,
#     'B': 0x1F,
#     'C': 0x4E,
#     'D': 0x3D,
#     'E': 0x4F,
#     'F': 0x47,
#     'G': 0x5E,
#     'H': 0x37,
#     'I': 0x30,
#     'J': 0x3C,
#     'K': 0x2F,
#     'L': 0x0E,
#     'M': 0x54,
#     'N': 0x15,
#     'O': 0x1D,
#     'P': 0x67,
#     'Q': 0x73,
#     'R': 0x05,
#     'S': 0x5B,
#     'T': 0x0F,
#     'U': 0x3E,
#     'V': 0x1C,
#     'W': 0x2A,
#     'X': 0x49,
#     'Y': 0x3B,
#     'Z': 0x25,
# }

AS1115_DIGIT_REGISTER = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]

NUMBERS = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47]

def nthdigit(value:int, idx:int):
    return value // 10**idx % 10

class AS1115:
    """
    :param ~busio.I2C i2c: The I2C bus object
    :param int|list|tuple address: The I2C addess(es).
    :param bool auto_write: True if the display should immediately change when
        set. If False, `show` must be called explicitly.
    :param float brightness: 0.0 - 1.0 default brightness level.
    """

    def __init__(
        self,
        i2c: I2C,
        address: int = 0x00,
        brightness: float = 1.0,
        n_digits: int = 4,
    ) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c, address)
        self._temp = bytearray(1)  # init bytearray
        self.n_digits = n_digits

        self._disp_test_mode = [None] * 7
        self._feature = [None] * 8
        self._digit = [None] * 8
        self._keyA = [None] * 8
        self._keyB = [None] * 8
        self._led_diag = [[None] * 8] * 8
        
        for i in range(8):
            if i != 3:
                self._feature[i] = i2c_bit.RWBit(register_address=AS1115_REGISTER['FEATURE'], bit=i)
            if i != 7:
                self._disp_test_mode[i] = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], bit=i)
            self._digit[i] = i2c_bits.RWBits(num_bits=4, register_address=AS1115_DIGIT_REGISTER[i], lowest_bit=0)
            self._keyA[i] = i2c_bit.ROBit(register_address=AS1115_REGISTER['KEY_A'], bit=i)
            self._keyB[i] = i2c_bit.ROBit(register_address=AS1115_REGISTER['KEY_B'], bit=i)
            for j in range(8):
                self._led_diag[i][j] = i2c_bit.ROBit(register_address=AS1115_LED_DIAG_REG[i], bit=i)
        
        self._scan_limit = i2c_bits.RWBits(num_bits=3, register_address=AS1115_REGISTER['SCAN_LIMIT'])
        self._led_short = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], 
                                bit=AS1115_DISPLAY_TEST_MODE['LED_SHORT'])
        self._led_short = i2c_bit.RWBit(register_address=AS1115_REGISTER['DISPLAY_TEST_MODE'], 
                                bit=AS1115_DISPLAY_TEST_MODE['LED_SHORT'])
        self._self_addressing = i2c_bit.RWBit(register_address=AS1115_REGISTER['SELF_ADDRESSING'], bit=0)
        self._shutdown_mode_unchanged = i2c_bit.RWBit(register_address=AS1115_REGISTER['SHUTDOWN_MODE'], bit=7)  # no reset
        self._shutdown_mode_normal = i2c_bit.RWBit(register_address=AS1115_REGISTER['SHUTDOWN_MODE'], bit=0)  # normal operation

        # --- start writing to chip --- #
        self._shutdown_mode_normal = 1
        self._shutdown_mode_unchanged = 0

        if address != 0x00:
            self._self_addressing = 1
            
        self._blink_rate = None
        self._brightness = None
        
        self._writeRegister(AS1115_REGISTER['DECODE_MODE'], 0x0F)  # this enables decoding on D0-D3

        self._writeRegister(AS1115_REGISTER['SCAN_LIMIT'], n_digits - 1)

        self.blink_rate = 0
        self.brightness = brightness

    def _write_cmd(self, byte: int) -> None:
        self._temp[0] = byte
        with self.i2c_device as bus_device:
            bus_device.write(self._temp)
    
    def _writeRegister(self, reg: int, value: int) -> None:
        self._temp[0] = reg
        self._temp.extend(value)
        with self.i2c_device as bus_device:
            bus_device.write(self._temp)

    def _readRegister(self, reg: int) -> int:
        self._write_cmd(reg)
        with self.i2c_device as bus_device:
            bus_device.write(bytes([reg]))
            result = bytearray(1)
            bus_device.readinto(result)
        return result

    def clear(self) -> None:
        n = self.n_digits
        for i in range(n):
            self._digit[i] = None  # is this how you clear a register?

    def clear_idx(self, idx: int) -> None:
        self._digit[idx] = None

    def display_idx(self, idx: int, value: int) -> None:
        # display int 0-9 on an individual digit
        self._digit[idx] = hex(value)

    def display_int(self, value: int) -> None:
        # display int on entire display
        n = self.n_digits
        for i in range(n):
            self._digit[i] = hex(nthdigit(value, i))

    def visualTest(self) -> None:
        self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['DISP_TEST']] = 1

    def ledTest(self) -> None:
        self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['LED_SHORT']] = 1
        self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['LED_OPEN']] = 1
        test_ongoing = True
        while test_ongoing:
            print('test ongoing...')
            test_ongoing = self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['LED_TEST']]
            time.sleep(1)
        result = self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['LED_GLOBAL']]
        if result is True:
            print('ledTest has detected an error')
        return result

    def rsetTest(self) -> None:
        rset_open = self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['RSET_OPEN']]
        rset_short = self._disp_test_mode[AS1115_DISPLAY_TEST_MODE['RSET_SHORT']]
        if rset_open is True:
            print('rsetTest has detected an open circuit')
        elif rset_short is True:
            print('rsetTest has detected a short circuit')
        return rset_open or rset_short

    @property
    def blink_rate(self) -> int:
        """The blink rate."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, rate: int) -> None:
        if rate not in [0, 1, 2]:
            raise ValueError("Blink rate must be an integer in the set: 0, 1, 2")
        self._blink_rate = rate
        if rate != 0:
            self._feature[AS1115_FEATURE['BLINK_ENABLE']] = 1
            self._feature[AS1115_FEATURE['BLINK_FREQ_SEL']] = rate - 1
        else:
            self._feature[AS1115_FEATURE['BLINK_ENABLE']] = 0

    @property
    def brightness(self) -> float:
        """The brightness. Range 0.0-1.0"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness: float) -> None:
        if not 0.0 <= brightness <= 1.0:
            raise ValueError(
                "Brightness must be a decimal number in the range: 0.0-1.0"
            )

        self._brightness = brightness
        duty_cycle = int(brightness * 15)
        self._writeRegister(AS1115_REGISTER['GLOBAL_INTENSITY'], hex(duty_cycle))

    