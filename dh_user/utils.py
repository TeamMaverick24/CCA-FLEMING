# -*- coding: utf-8 -*-
import pytz

TIMEZONE_CONTINENT = "Asia"

DEFAULT_TIMEZONE = "Asia/Kolkata"

SYSTEM_TIMEZONE = "Asia/Kolkata"


def get_timezones():
    """
    Return timezones. Only one continent will suffice for the scope of the exercise.
    """
    return tuple([(x, x) for x in pytz.all_timezones if TIMEZONE_CONTINENT in x])


def normalize_to_utc(time, timezone):
    """
    Convert naive time into given timezone, then UTC
    """
    utct = pytz.timezone(u'UTC')
    tzt = pytz.timezone(timezone)

    return tzt.localize(time).astimezone(utct)

