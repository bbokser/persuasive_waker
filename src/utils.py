from math import floor

colors = {
    "white": 0xFFFFFF,
    "black": 0x000000,
    # 'blue':   0x0000FF,
    # 'green':  0x00FF00,
    # 'red':    0xFF0000,
    # 'yellow': 0xFFFF00,
    # 'orange': 0xFFA500
}

weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
month = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
number_suffix = {
    0: "th",
    1: "st",
    2: "nd",
    3: "rd",
    4: "th",
    5: "th",
    6: "th",
    7: "th",
    8: "th",
    9: "th",
}

tones = {"c4": 262, "d4": 294, "e4": 330, "f4": 359, "g4": 392, "a4": 440, "b4": 494}


def leapyear(year: int) -> bool:
    # check whether a given year is a leap year.
    """
    https://www.rmg.co.uk/stories/topics/which-years-are-leap-years-can-you-have-leap-seconds
    "To be a leap year, the year number must be divisible by four
    except for end-of-century years, which must be divisible by 400"
    """
    if (year % 4) != 0:
        # years not divisible by 4 are not leap years
        return False
    if (year % 100) != 0:
        # years divisible by 4 but not 100 are leap years
        return True
    if (year % 400) != 0:
        # years divisible by 4 and 100 but not 400 are not leap years
        return False
    return True


def get_max_day(year: int, month: int) -> int:
    # return the number of days in the given month and for the given year
    # https://stackoverflow.com/questions/15148534/calculating-number-of-days-in-a-month-based-on-leap-year
    assert 1 <= month <= 12
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        # month is February
        if leapyear(year):
            return 29
        else:
            return 28


def wrap_to_range(x: int, a: int, b: int) -> int:
    """
    x: the value to wrap
    a <= x <= b
    """
    return int((x - a) % (b - a + 1) + a)


def clip(input: float, min: float, max: float) -> float:
    assert min < max
    if input < min:
        return min
    elif input > max:
        return max
    else:
        return input


def translate(percent: float, min: float, max: float) -> float:
    # map range from 0 to 1 to a range from spec'd min and max
    diff = max - min
    return percent * diff + min


def percentize(value: float, min: float, max: float) -> float:
    # map range from from spec'd min and max to range from 0 to 1
    diff = max - min
    return (clip(value, min, max) - min) / diff
