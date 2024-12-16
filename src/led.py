import pwmio


class LED:
    def __init__(self, pin, brightness=0):
        self.led = pwmio.PWMOut(pin, frequency=5000, duty_cycle=0)
        self.set_brightness(brightness)

    def set_brightness(self, percent: float):
        assert 0 <= percent <= 1
        self._saved_duty_cycle = int(percent * 2 * 65535)

    def on(self):
        self.led.duty_cycle = self._saved_duty_cycle

    def off(self):
        self.led.duty_cycle = 0
