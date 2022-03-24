import logging
import re
from datetime import datetime, timedelta

LOGGER = logging.getLogger('dtutils')


def getCutoffTime(cutoff: str):
    """
    Determine a cutoff time based on the current time and a given time
    difference.

    :param str cutoff: a string indicating the time difference. e.g. '-2 hours'
    would indicate a time two hours before the current time

    :returns: :class:`datetime.datetime` object

    """

    regex = re.compile(r'^((?P<weeks>-?[\.\d]+?)\s+(w|weeks))? *'
                       r'^((?P<days>-?[\.\d]+?)\s+(d|days))? *'
                       r'((?P<hours>-?[\.\d]+?)\s+(h|hours))? *'
                       r'((?P<minutes>-?[\.\d]+?)\s+(m|min))? *'
                       r'((?P<seconds>-?[\.\d]+?)\s+(s|sec)?)?$')

    parts = regex.match(cutoff)
    assert parts is not None
    time_params = {name: float(param)
                   for name, param in parts.groupdict().items() if param}
    delta = timedelta(**time_params)
    cutoffTime = datetime.now() + delta
    return cutoffTime


def currentCycle(now=datetime.utcnow(), cycle=6, delay=3):
    """
    Calculate the forecast start time based on the current datetime, 
    how often the forecast updates (the cycle) and the delay between
    the forecast time and when it becomes available

    :param now: `datetime` representation of the "current" time. Default is
    the current UTC datetime
    :param int cycle: The cycle of forecasts, in hours
    :param int delay: Delay between the initial time of the forecast and when
    the forecast is published (in hours)

    :returns: `datetime` instance of the most recent forecast
    """
    LOGGER.debug(f"Current time: {now}")
    fcast_time = now
    if now.hour < delay:
        # e.g. now.hour = 01 and delay = 3
        fcast_time = fcast_time - timedelta(cycle/24)
        fcast_hour = (fcast_time.hour // cycle) * cycle
        fcast_time = fcast_time.replace(hour=fcast_hour, minute=0,
                                        second=0, microsecond=0)
    else:
        fcast_hour = ((fcast_time.hour - delay) // cycle) * cycle
        fcast_time = fcast_time.replace(hour=fcast_hour, minute=0,
                                        second=0, microsecond=0)
    LOGGER.debug(f"Forecast time: {fcast_time}")
    return fcast_time


def roundTime(dt: datetime = None, roundTo: int = 60) -> datetime:
    """
    Round a datetime object to any time lapse in seconds. We see occasional
    issues with the rounding of datetime values in the netcdf files, which can
    play havoc with timestamp strings.

    :param dt: datetime.datetime object, default now.
    :param roundTo: Closest number of seconds to round to, default 1 minute.

    :returns: `datetime` object rounded appropriately
    """
    if dt is None:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None) -
               dt.replace(hour=0, minute=0, second=0)).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0, rounding - seconds,
                                   -dt.microsecond)