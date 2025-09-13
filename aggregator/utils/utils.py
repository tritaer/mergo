from datetime import datetime
from datetime import timedelta
import pytz


def day_duration(day: datetime) -> int:
    """
    Returns the duration of a day in hours (24, 23 or 25 hours).
    """
    d = day.replace(hour=0, minute=0, second=0, microsecond=0)
    # convert kyiv to UTC
    start_utc = pytz.timezone('Europe/Kyiv').localize(d).astimezone(pytz.timezone('UTC'))
    end_utc = (pytz.timezone('Europe/Kyiv').localize(d + timedelta(days=1))).astimezone(pytz.timezone('UTC'))
    if start_utc.hour == end_utc.hour:
        return 24
    elif start_utc.hour < end_utc.hour:
        return 25
    else:
        return 23