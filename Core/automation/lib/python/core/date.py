"""
The Date module provides data types and methods for working with DateTime items.

Types
=====

    There are three DateTime types made available by this module:

    .. code-block::

        from core.date import javaDateTime # recommended
        from core.date import pythonDateTime
        from core.date import jodaDateTime

    It is recommended that you use ``javaDateTime`` from this module for all
    operations involving dates or ``DateTime`` items. See the documentation for
    `java.time.ZonedDateTime <https://docs.oracle.com/javase/8/docs/api/java/time/ZonedDateTime.html>`_
    for more information about its useage.

    .. warning::

        The use of ``jodaDateTime`` for new rules is not recommended as the Joda
        package may not be available in future versions of openHAB. You will
        find that ``javaDateTime`` has many functions in common with
        ``jodaDateTime``, which should make transitioning fairly straight
        forward.

    All of the methods in this module can accept any of the following DateTime
    types:

    .. code-block::

        java.time.ZonedDateTime
        java.time.LocalDateTime
        java.util.Calendar
        java.util.Date
        org.joda.time.DateTime
        datetime.datetime (Python)
        org.eclipse.smarthome.core.library.types.DateTimeType
        org.openhab.core.library.types.DateTimeType

Functions
=========
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
    DateTime value for output. The default format string follows the same
    ISO8601 format used in openHAB.

    Examples:
        .. code-block::

            sendCommand("date_item", format_date(date_value))
            log.info("The time is currently: {}".format(format_date(javaDateTime.now())))

    Args:
        value: Any known DateTime value.
        format_string (str): Pattern to format ``value`` with.
            See `java.time.format.DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html>`_
            for format string tokens.

    Returns:
        | A string representation of ``value`` according to ``format_string``.
        | If ``value`` does not have timezone information, the system default
          will be used.
    """
    return to_java_zoneddatetime(value).format(DateTimeFormatter.ofPattern(format_string))

def days_between(value_from, value_to, calendar_days=False):
    """Returns the number of days between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_days = days_between(items["date_item"], javaDateTime.now())

    Args:
        value_from: Value to start from.
        value_to: Value to measure to.
        calendar_days (bool): If ``True`` will return calendar days between
            instead of 24-hour periods between.
    """
    if calendar_days:
        return DAYS.between(to_java_zoneddatetime(value_from).toLocalDate().atStartOfDay(), to_java_zoneddatetime(value_to).toLocalDate().atStartOfDay())
    else:
        return DAYS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def hours_between(value_from, value_to):
    """Returns the number of hours between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_hours = hours_between(items["date_item"], javaDateTime.now())

    Args:
        value_from: Value to start from.
        value_to: Value to measure to.
    """
    return HOURS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def minutes_between(value_from, value_to):
    """Returns the number of minutes between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_minutes = minutes_between(items["date_item"], javaDateTime.now())

    Args:
        value_from: Value to start from.
        value_to: Value to measure to.
    """
    return MINUTES.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def seconds_between(value_from, value_to):
    """Returns the number of seconds between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_seconds = seconds_between(items["date_item"], javaDateTime.now())

    Args:
        value_from: Value to start from.
        value_to: Value to measure to.
    """
    return SECONDS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def to_java_zoneddatetime(value):
    """Converts any known DateTime type to a ``java.time.ZonedDateTime`` type.
    This is the same type as ``date.javaDateTime``.

    Examples:
        .. code-block::

            java_time = to_java_zoneddatetime(items["date_item"])

    Args:
        value: Any known DateTime value.

    Returns:
        | A ``java.time.ZonedDateTime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: If type of ``value`` is not recognized by this package.
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
    This is the same type as ``date.pythonDateTime``.

    Examples:
        .. code-block::

            python_time = to_python_datetime(items["date_item"])

    Args:
        value: Any known DateTime value.

    Returns:
        | A Python ``datetime.datetime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: If type of ``value`` is not recognized by this package.
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
        offset (int): Timezone offset from UTC in minutes.
        name (str): Display name of this instance.
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
    This is the same type as ``date.jodaDateTime``.

    Examples:
        .. code-block::

            joda_time = to_joda_datetime(items["date_item"])

    Args:
        value: Any known DateTime value.

    Returns:
        | An ``org.joda.time.DateTime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: If type of ``value`` is not recognized by this package.
    """
    if isinstance(value, jodaDateTime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    return jodaDateTime(
        value_zoneddatetime.toInstant().toEpochMilli(),
        jodaDateTimeZone.forID(value_zoneddatetime.getZone().getId())
    )

def to_java_calendar(value):
    """Converts any known DateTime type to a ``java.util.Calendar`` type.

    Examples:
        .. code-block::

            calendar_time = to_java_calendar(items["date_item"])

    Args:
        value: Any known DateTime value.

    Returns:
        | A ``java.util.Calendar`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: If type of ``value`` is not recognized by this package.
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
