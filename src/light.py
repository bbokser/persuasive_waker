import utils
from clock import Clock


class Light:
    def __init__(
        self,
        clock: Clock,
        start_time: float = 7.5,
        end_time: float = 19.5,
        siesta: int = 16,
        brightness_min: float = 0.15,
        brightness_max: float = 1.0,
    ):
        """
        function for light level. Should gradually get brighter until peak

        Parameters:
            clock: Clock class object
            start_time: time at which light turns on
            end_time: time at which light turns off
            siesta: hour at which siesta occurs
        """
        self.clock = clock

        assert end_time > start_time
        assert end_time < 24.0
        self.start_time = start_time
        self.end_time = end_time
        self.siesta = siesta
        # time at which brightness peaks
        self.midday = (start_time + end_time) / 2
        # how many hours the light should be on for
        self.timespan = end_time - start_time
        # brightness range, must be between 0 and 1
        self.brightness_min = brightness_min
        self.brightness_max = brightness_max

    def get_brightness(self) -> float:
        if int(self.clock.get_hour()) == self.siesta:
            # 4 o'clock siesta
            return 0.0
        else:
            # difference in hours between now and peak
            delta_hours = abs(self.clock.get_delta_hours(self.midday))
            # brightness
            brightness = utils.percentize(
                self.midday / 2 - delta_hours, 0.0, self.timespan / 2
            )
            brightness = utils.translate(brightness, self.brightness_min, self.brightness_max)
            # prevent high-pitched whine
            if 0.0 < brightness < self.brightness_min + 0.01:
                brightness = 0.0
            return brightness

    def get_info_str(self) -> str:
        return (
            "{:.1f}".format(self.start_time)
            + "-"
            + "{:.1f}".format(self.end_time)
            + ", value="
            + "{:.2f}".format(self.get_brightness())
        )
