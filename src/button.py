import digitalio


class HoldButton:
    """
    Checks if button is currently being pressed
    """

    def __init__(self, pin):
        self.button_prev = False
        self.button = digitalio.DigitalInOut(pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP

    def get_value(self) -> bool:
        return self.button.value


class ScanButton:
    """
    Debounces button presses from keyscan
    """

    def __init__(self) -> None:
        self.prev_pressed = False

    def update(self, pressed: bool) -> bool:
        # Call once per loop iteration with the current boolean state
        pressed = bool(pressed)
        just_pressed = pressed and not self.prev_pressed
        self.prev_pressed = pressed
        return just_pressed
