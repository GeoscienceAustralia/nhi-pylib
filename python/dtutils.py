import logging
from datetime import datetime, timedelta

LOGGER = logging.getLogger('dtutils')


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
