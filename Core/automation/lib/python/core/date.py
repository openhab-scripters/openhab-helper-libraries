"""
Date/time utilities for converting between the several different types used by
openHAB. It can also format any of these types for sending to an openHAB Item
using ``format_date(value)``, which will return the date as a string in the 
correct format. There are also some convenience functions for determining the
span between two datetimes. ``days_between``, ``hours_between``,
``minutes_between``, and ``seconds_between`` will return the number of whole
units of each unit of time between the two datetimes passed. They will return
negative numbers if ``value_from`` is after ``value_to``. See
`java.time.temporal.ChronoUnit <https://docs.oracle.com/javase/8/docs/api/java/time/temporal/ChronoUnit.html>`_
if you want more information.

This module accepts any of the following DateTime types:

.. code-block::

    java.time.ZonedDateTime
    java.time.LocalDateTime
    java.util.Calendar
    java.util.Date
    org.joda.time.DateTime
    datetime.datetime (Python)
    org.eclipse.smarthome.core.library.types.DateTimeType
    org.openhab.core.library.types.DateTimeType
"""

import sys
import datetime

if 'org.eclipse.smarthome.automation' in sys.modules or 'org.openhab.core.automation' in sys.modules:
    # Workaround for Jython JSR223 bug where dates and datetimes are converted
    # to java.sql.Date and java.sql.Timestamp
    def remove_java_converter(clazz):
        if hasattr(clazz, '__tojava__'):
            del clazz.__tojava__
    remove_java_converter(datetime.date)
    remove_java_converter(datetime.datetime)

from java.time import LocalDateTime as javaLocalDateTime, ZonedDateTime as javaDateTime
from java.time import ZoneId as javaZoneId, ZoneOffset as javaZoneOffset
from java.time.format import DateTimeFormatter
from java.time.temporal.ChronoUnit import DAYS, HOURS, MINUTES, SECONDS
from datetime import datetime as pythonDateTime, date as pythonDate
from org.joda.time import DateTime as jodaDateTime, DateTimeZone as jodaDateTimeZone
from java.util import Calendar as utilCalendar, Date as utilDateTime, TimeZone as utilTimeZone
from org.eclipse.smarthome.core.library.types import DateTimeType as eclipseDateTime

try:
    # if the compat1.x bundle is not installed the 1.x DateTimeType is not available
    from org.openhab.core.library.types import DateTimeType as legacyDateTime
except:
    pass

__all__ = [
    "format_date",
    "days_between", "hours_between", "minutes_between", "seconds_between",
    "to_java_zoneddatetime", "toJTime", "javaDateTime",
    "to_java_calendar", "toJCal",
    "to_python_datetime", "toPyDT", "pythonDateTime", "pythonTimezone",
    "to_joda_datetime", "toJodaDT", "jodaDateTime"
]


def format_date(value, format_string="yyyy-MM-dd'T'HH:mm:ss.SSxx"):
    """Returns string of ``value`` formatted according to ``format_string``.

    This function can be used when updating Items in openHAB or to format any
    DateTime value for output.

    Examples:
        .. code-block::

            sendCommand("item_name", date.format_date(date_value))

    Args:
        value: any known DateTime value.
        format_string (string): pattern to format ``value`` with.
            See `java.time.format.DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html>`_
            for format string tokens.
    """
    return to_java_zoneddatetime(value).format(DateTimeFormatter.ofPattern(format_string))

def days_between(value_from, value_to, calendar_days=False):
    '''Returns number of whole days between value_from and value_to. Setting 
    calendar_days=True will provide the number of calendar days, rather than 
    24 hour intervals.
    Accepts any date type used by this module'''
    if calendar_days:
        return DAYS.between(to_java_zoneddatetime(value_from).toLocalDate().atStartOfDay(), to_java_zoneddatetime(value_to).toLocalDate().atStartOfDay())
    else:
        return DAYS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def hours_between(value_from, value_to):
    """Returns ``long`` of whole hours between ``value_from`` and ``value_to``."""
    return HOURS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def minutes_between(value_from, value_to):
    """Returns ``long`` of whole minutes between ``value_from`` and ``value_to``."""
    return MINUTES.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def seconds_between(value_from, value_to):
    """Returns ``long`` of whole seconds between ``value_from`` and ``value_to``."""
    return SECONDS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def to_java_zoneddatetime(value):
    """Converts any known DateTime type to a ``java.time.ZonedDateTime`` type.

    Args:
        value: any known DateTime value.

    Returns:
        | A ``java.time.ZonedDateTime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: type of ``value`` is not recognized by this package.
    """
    if isinstance(value, javaDateTime):
        return value
    timezone_id = javaZoneId.systemDefault()
    # java.time.LocalDateTime
    if isinstance(value, javaLocalDateTime):
        return value.atZone(timezone_id)
    # python datetime
    if isinstance(value, pythonDateTime):
        if value.tzinfo is not None:
            timezone_id = javaZoneId.ofOffset("GMT", javaZoneOffset.ofTotalSeconds(int(value.utcoffset().total_seconds())))
        return javaDateTime.of(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond * 1000,
            timezone_id
        )
    # java.util.Calendar
    if isinstance(value, utilCalendar):
        return javaDateTime.ofInstant(value.toInstant(), javaZoneId.of(value.getTimeZone().getID()))
    # java.util.Date
    if isinstance(value, utilDateTime):
        return javaDateTime.ofInstant(value.toInstant(), javaZoneId.ofOffset("GMT", javaZoneOffset.ofHours(0 - value.getTimezoneOffset() / 60)))
    # Joda DateTime
    if isinstance(value, jodaDateTime):
        return value.toGregorianCalendar().toZonedDateTime()
    # openHAB DateTimeType
    if isinstance(value, eclipseDateTime):
        return to_java_zoneddatetime(value.calendar)
    # openHAB 1.x DateTimeType
    if legacyDateTime and isinstance(value, legacyDateTime):
        return to_java_zoneddatetime(value.calendar)

    raise TypeError("Unknown type: {}".format(str(type(value))))

def to_python_datetime(value):
    """Converts any known DateTime type to a Python ``datetime.datetime`` type.

    Args:
        value: any known DateTime value.

    Returns:
        | A Python ``datetime.datetime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: type of ``value`` is not recognized by this package.
    """
    if isinstance(value, pythonDateTime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    return pythonDateTime(
        value_zoneddatetime.getYear(),
        value_zoneddatetime.getMonthValue(),
        value_zoneddatetime.getDayOfMonth(),
        value_zoneddatetime.getHour(),
        value_zoneddatetime.getMinute(),
        value_zoneddatetime.getSecond(),
        int(value_zoneddatetime.getNano() / 1000),
        pythonTimezone(int(value_zoneddatetime.getOffset().getTotalSeconds() / 60))
    )

class pythonTimezone(datetime.tzinfo):
    """Python tzinfo with ``offset`` in minutes and name ``name``.

    Args:
        offset (int): timezone offset from UTC in minutes.
        name (str): display name of this instance.
    """

    def __init__(self, offset=0, name=""):
        self.__offset = offset
        self.__name = name

    def utcoffset(self, value):
        return datetime.timedelta(minutes = self.__offset)

    def tzname(self, value):
        return self.__name

    def dst(self, value):
        return datetime.timedelta(0)

def to_joda_datetime(value):
    """Converts any known DateTime type to a ``org.joda.time.DateTime`` type.

    Args:
        value: any known DateTime value.

    Returns:
        | An ``org.joda.time.DateTime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: type of ``value`` is not recognized by this package.
    """
    if isinstance(value, jodaDateTime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    return jodaDateTime(
        value_zoneddatetime.toInstant().toEpochMilli(),
        jodaDateTimeZone.forID(value_zoneddatetime.getZone().getId())
    )

def to_java_calendar(value):
    """Converts any known DateTime type to a ``java.util.calendar`` type.

    Args:
        value: any known DateTime value.

    Returns:
        | A ``java.util.calendar`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: type of ``value`` is not recognized by this package.
    """
    if isinstance(value, utilCalendar):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    new_calendar = utilCalendar.getInstance(utilTimeZone.getTimeZone(value_zoneddatetime.getZone().getId()))
    new_calendar.set(utilCalendar.YEAR, value_zoneddatetime.getYear())
    new_calendar.set(utilCalendar.MONTH, value_zoneddatetime.getMonthValue() - 1)
    new_calendar.set(utilCalendar.DAY_OF_MONTH, value_zoneddatetime.getDayOfMonth())
    new_calendar.set(utilCalendar.HOUR_OF_DAY, value_zoneddatetime.getHour())
    new_calendar.set(utilCalendar.MINUTE, value_zoneddatetime.getMinute())
    new_calendar.set(utilCalendar.SECOND, value_zoneddatetime.getSecond())
    new_calendar.set(utilCalendar.MILLISECOND, int(value_zoneddatetime.getNano() / 1000000))
    return new_calendar

# aliases
toJTime = to_java_zoneddatetime     #: alias of ``to_java_zoneddatetime``.
toJCal = to_java_calendar           #: alias of ``to_java_calendar``.
toPyDT = to_python_datetime         #: alias of ``to_python_datetime``.
toJodaDT = to_joda_datetime         #: alias of ``to_joda_datetime``.
