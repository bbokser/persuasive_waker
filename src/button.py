import digitalio


class PinButton:
    """
    Debounces button presses from pin
    """

    def __init__(self, pin):
        self.button_prev = False
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP

    def update(self) -> bool:
        # this must run every timestep to work
        if self.button_prev is True and self._get_button() is False:
            # button was previously pressed, is no longer pressed
            self.button_prev = False
            return True
        self.button_prev = self._get_button()
        return False

    def _get_button(self) -> bool:
        return not self.button.value


class ScanButton:
    """
    Debounces button presses from keyscan
    """

    def __init__(self):
        self.button_prev = False
        self.button = False

    def update(self, input) -> bool:
        # this must run every timestep to work
        if self.button_prev is True and input is False:
            # button was previously pressed, is no longer pressed
            self.button_prev = False
            return True
        self.button_prev = input
        return False
