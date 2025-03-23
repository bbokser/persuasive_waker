from adafruit_bus_device import i2c_device
from adafruit_register import i2c_bit
from adafruit_register import i2c_bits

# from typing import Union, List, Tuple, Optional
from busio import I2C
import time

AS1115_CLEAR = 15  # BCD
AS1115_REGISTER = {
    "DECODE_MODE": 0x09,  # Enables decoding on selected digits
    "GLOBAL_INTENSITY": 0x0A,  # Sets the entire display intensity
    "SCAN_LIMIT": 0x0B,  # Controls how many digits are to be displayed
    "SHUTDOWN": 0x0C,  #
    "SELF_ADDRESSING": 0x2D,  # Uses 2 of the 16 keys to change the device's address
    "FEATURE": 0x0E,  # Enables various features such as clock mode and blinking
    "DISPLAY_TEST_MODE": 0x0F,  # Detects open or shorted LEDs
    "DIG01_INTENSITY": 0x10,  # Sets the display intensity for digit 0 and 1
    "DIG23_INTENSITY": 0x11,  # Sets the display intensity for digit 2 and 3
    "DIG45_INTENSITY": 0x12,  # Sets the display intensity for digit 4 and 5
    "DIG67_INTENSITY": 0x13,  # Sets the display intensity for digit 6 and 7
    "KEY_A": 0x1C,  # Gets the result of the debounced keyscan for KEYA
    "KEY_B": 0x1D,  # Gets the result of the debounced keyscan for KEYB
}

AS1115_SHUTDOWN_MODE = {
    "SHUTDOWN_MODE": 0x00,  #  Shutdown and reset FEATURE register to default settings.
    "NORMAL_OPERATION": 0x01,  #  Resume operation and reset FEATURE register to default settings.
    "RESET_FEATURE": 0x00,  #  FEATURE register is resetted to default settings.
    "PRESERVE_FEATURE": 0x80,  #  FEATURE register is unchanged.
}

AS1115_DECODE_SEL = {
    "CODE_B_DECODING": 0x00,
    "HEX_DECODING": 0x01,
}

AS1115_DISPLAY_TEST_MODE = {
    "DISP_TEST": 0,  #  Optical display test.
    "LED_SHORT": 1,  #  Starts a test for shorted LEDs.
    "LED_OPEN": 2,  #  Starts a test for open LEDs.
    "LED_TEST": 3,  #  Indicates an ongoing open/short LED test.
    "LED_GLOBAL": 4,  #  Indicates that the last open/short LED test has detected an error.
    "RSET_OPEN": 5,  #  Checks if external resistor Rset is open.
    "RSET_SHORT": 6,  #  Checks if external resistor Rset is shorted.
}

AS1115_DIGIT_REGISTER = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
AS1115_LED_DIAG_REG = [0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B]
NUMBERS = [
    0x7E,
    0x30,
    0x6D,
    0x79,
    0x33,
    0x5B,
    0x5F,
    0x70,
    0x7F,
    0x7B,
    0x77,
    0x1F,
    0x4E,
    0x3D,
    0x4F,
    0x47,
]
LETTERS = {
    "A": 2 | 4 | 64 | 32 | 16,
    "b": 2 | 4 | 8 | 16 | 1,
    "C": 2 | 4 | 64 | 8,
    "d": 4 | 8 | 16 | 32 | 1,
    "E": 2 | 4 | 8 | 64 | 1,
    "F": 2 | 4 | 64 | 1,
    "h": 2 | 4 | 1 | 16,
}


def nth(value: int, idx: int):
    return value // 10**idx % 10


def reversed_nth(value: int, idx: int, n: int):
    # n is the number of digits
    idx_reversed = n - 1 - idx
    return nth(value, idx_reversed)


def check_brightness_value(value: int) -> None:
    if not 0 <= value <= 15:
        raise ValueError("Brightness must be an int in the range: 0 - 15")


class AS1115_REG:
    # enables external clock
    feature_clock_active = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=0
    )
    # resets all control registers except for feature register
    feature_reset_all = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=1
    )
    # enable Code-B or HEX decoding for the selected digits
    feature_decode_sel = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=2
    )
    # enable blinking
    feature_blink_enable = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=4
    )
    # set blinking frequency
    feature_blink_freq_sel = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=5
    )
    # sync blinking with LD/CS pin
    feature_blink_sync = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=6
    )
    # whether to start blinking w/ display turned on or off
    feature_blink_start = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["FEATURE"], bit=7
    )

    #  Optical display test.
    disp_test_visual = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=0
    )
    #  Starts a test for shorted LEDs.
    disp_test_led_short = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=1
    )
    #  Starts a test for open LEDs.
    disp_test_led_open = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=2
    )
    #  Indicates an ongoing open/short LED test.
    disp_test_led_test = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=3
    )
    #  Indicates that the last open/short LED test has detected an error.
    disp_test_led_global = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=4
    )
    #  Checks if external resistor Rset is open.
    disp_test_rset_open = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=5
    )
    #  Checks if external resistor Rset is shorted.
    disp_test_rset_short = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["DISPLAY_TEST_MODE"], bit=6
    )

    global_intensity = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_REGISTER["GLOBAL_INTENSITY"], lowest_bit=0
    )
    intensity_01 = i2c_bits.RWBits(
        num_bits=8, register_address=AS1115_REGISTER["DIG01_INTENSITY"], lowest_bit=0
    )
    intensity_23 = i2c_bits.RWBits(
        num_bits=8, register_address=AS1115_REGISTER["DIG23_INTENSITY"], lowest_bit=0
    )

    scan_limit = i2c_bits.RWBits(
        num_bits=3, register_address=AS1115_REGISTER["SCAN_LIMIT"], lowest_bit=0
    )
    decode_mode = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_REGISTER["DECODE_MODE"], lowest_bit=0
    )
    self_addressing = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["SELF_ADDRESSING"], bit=0
    )
    shutdown_mode_unchanged = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["SHUTDOWN"], bit=7
    )  # no reset
    shutdown_mode_normal = i2c_bit.RWBit(
        register_address=AS1115_REGISTER["SHUTDOWN"], bit=0
    )  # normal operation

    digit_0 = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_DIGIT_REGISTER[0], lowest_bit=0
    )
    digit_1 = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_DIGIT_REGISTER[1], lowest_bit=0
    )
    digit_2 = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_DIGIT_REGISTER[2], lowest_bit=0
    )
    digit_3 = i2c_bits.RWBits(
        num_bits=4, register_address=AS1115_DIGIT_REGISTER[3], lowest_bit=0
    )

    keyA = [None] * 8
    # keyB = [None] * 8
    for i in range(8):
        keyA[i] = i2c_bit.ROBit(register_address=AS1115_REGISTER["KEY_A"], bit=i)
        # keyB[i] = i2c_bit.ROBit(register_address=AS1115_REGISTER['KEY_B'], bit=i)

    led_diag = [[[None] for i in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            led_diag[i][j] = i2c_bit.ROBit(
                register_address=AS1115_LED_DIAG_REG[i], bit=i
            )

    def __init__(self, i2c: I2C, address: int = 0x00) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c, address)

    def set_digit(self, idx: int, value: int) -> None:
        if idx == 0:
            self.digit_0 = value
        elif idx == 1:
            self.digit_1 = value
        elif idx == 2:
            self.digit_2 = value
        elif idx == 3:
            self.digit_3 = value
        else:
            raise ValueError("Digit specified does not exist")


class AS1115:
    """
    :param ~busio.I2C i2c: The I2C bus object
    :param int|list|tuple address: The I2C addess(es).
    :param bool auto_write: True if the display should immediately change when
        set. If False, `show` must be called explicitly.
    :param int brightness: 0 - 15 default brightness level.
    """

    def __init__(
        self,
        i2c: I2C,
        address: int = 0x00,
        brightness: int = 2,
        n_digits: int = 4,
    ) -> None:
        self.device = AS1115_REG(i2c, address)
        self.n_digits = n_digits

        # --- start writing to chip --- #
        if address != 0x00:
            self.device.self_addressing = 1

        self._blink_rate = None
        self._brightness = None
        self.keyscan = [None] * 8

        self.enable_decode()
        self.device.feature_decode_sel = 0  # set to code-B
        self.device.scan_limit = 6
        self.device.shutdown_mode_unchanged = 0
        self.device.shutdown_mode_normal = 1

        self.blink_rate = 0
        self.brightness = brightness

    def enable_decode(self):
        # this enables decoding on D0, D1, D2, D3
        self.device.decode_mode = 0xF

    def disable_decode(self):
        self.device.decode_mode = 0x0

    def scan_keys(self) -> list:
        for i in range(8):
            self.keyscan[i] = self.device.keyA[i].__get__(obj=self.device)
        return [not x for x in self.keyscan]  # flip the bool values

    def clear(self) -> None:
        n = self.n_digits
        for i in range(n):
            self.clear_idx(i)

    def clear_idx(self, idx: int) -> None:
        self.device.set_digit(idx, AS1115_CLEAR)

    def display_idx(self, idx: int, value: int) -> None:
        # display int 0-9 on an individual digit
        self.device.set_digit(idx, value)

    def display_int(self, value: int) -> None:
        # display int on entire display
        value = int("{:04d}".format(value))
        for i in range(self.n_digits):
            self.device.set_digit(i, reversed_nth(value, i, self.n_digits))

    def display_half(self, value: int) -> None:
        self.clear_idx(0)
        self.clear_idx(1)
        self.display_idx(2, nth(value, 1))
        self.display_idx(3, nth(value, 0))

    def display_hourmin(self, hour: int, minute: int) -> None:
        self.display_idx(0, nth(hour, 1))
        self.display_idx(1, nth(hour, 0))
        self.display_idx(2, nth(minute, 1))
        self.display_idx(3, nth(minute, 0))

    def display_letter(self, letter: str) -> None:
        # show single letter
        self.disable_decode()
        self.device.set_digit(0, 0)
        self.device.set_digit(1, 0)
        self.device.set_digit(2, 0)
        self.device.set_digit(3, LETTERS[letter])

    def display_fullweek(self) -> None:
        # show 7 bars representing 7 days
        self.disable_decode()
        # 4 decimal = 100 binary -> seg C
        # 16 decimal = 10000 binary -> seg E
        self.device.set_digit(0, 16)
        self.device.set_digit(1, 4 | 16)
        self.device.set_digit(2, 4 | 16)
        self.device.set_digit(3, 4 | 16)

    def display_weekend(self) -> None:
        # show 2 bars representing sat-sun
        self.disable_decode()
        self.device.set_digit(0, 16)
        self.device.set_digit(1, 0)
        self.device.set_digit(2, 0)
        self.device.set_digit(3, 16)

    def display_workdays(self) -> None:
        # show 5 bars representing mon-fri
        self.disable_decode()
        self.device.set_digit(0, 0)
        self.device.set_digit(1, 4 | 16)
        self.device.set_digit(2, 4 | 16)
        self.device.set_digit(3, 4)

    def visualTest(self) -> None:
        self.device.disp_test_visual = 1

    def ledTest(self) -> None:
        self.device.disp_test_led_short = 1
        self.device.disp_test_led_open = 1
        test_ongoing = True
        while test_ongoing:
            print("test ongoing...")
            test_ongoing = self.device.disp_test_led_test
            time.sleep(1)
        result = self.device.disp_test_led_global
        if result is True:
            print("ledTest has detected an error")
            for i in range(8):
                for j in range(8):
                    led_diag_i_j = self.device.led_diag[i][j].__get__(obj=self.device)
                    print(i, j, led_diag_i_j)
        return result

    def rsetTest(self) -> None:
        rset_open = self.device.disp_test_rset_open
        rset_short = self.device.disp_test_rset_short
        if rset_open is True:
            print("rsetTest has detected an open circuit")
        elif rset_short is True:
            print("rsetTest has detected a short circuit")
        return rset_open or rset_short

    def wink_left(self, bool: bool) -> None:
        value = bool * self.brightness
        self.device.intensity_01 = value | (value << 4)

    def wink_right(self, bool: bool) -> None:
        value = bool * self.brightness
        self.device.intensity_23 = value | (value << 4)

    def unwink(self) -> None:
        # reset winkness
        self.brightness = self.brightness

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
            self.device.feature_blink_enable = 1
            self.device.feature_blink_freq_sel = rate - 1
        else:
            self.device.feature_blink_enable = 0

    @property
    def brightness(self) -> int:
        """The brightness. Range 0 - 15"""
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        check_brightness_value(value)
        self._brightness = int(value)
        self.device.global_intensity = self._brightness
