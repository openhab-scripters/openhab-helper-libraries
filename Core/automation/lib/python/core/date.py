# pylint: disable=super-init-not-called
"""
This module provides functions for date and time conversions. The functions in
this module can accept any of the following date types:

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
__all__ = [
    "format_date", "days_between", "hours_between", "minutes_between",
    "seconds_between", "to_java_zoneddatetime", "to_java_calendar",
    "to_python_datetime", "to_joda_datetime", "human_readable_seconds"
]

try:
    import typing as t
except:
    pass

import sys
import datetime
import inspect

from core.log import getLogger

from java.time import LocalDateTime, ZonedDateTime
from java.time import ZoneId, ZoneOffset
from java.time.format import DateTimeFormatter
from java.time.temporal import ChronoUnit
from java.util import Calendar, Date, TimeZone

DAYS = ChronoUnit.DAYS
HOURS = ChronoUnit.HOURS
MINUTES = ChronoUnit.MINUTES
SECONDS = ChronoUnit.SECONDS

try:
    from org.joda.time import DateTime as JodaDateTime
    from org.joda.time import DateTimeZone as JodaDateTimeZone
except:
    # OH3 does not have Joda Time
    JodaDateTime = None
    JodaDateTimeZone = None

try:
    # OH2.x compat1x or OH3
    from org.openhab.core.library.types import DateTimeType
    from org.openhab.core.library.items import DateTimeItem
except:
    DateTimeType = None
    DateTimeItem = None

try:
    from org.eclipse.smarthome.core.library.types import DateTimeType as EclipseDateTimeType
    from org.eclipse.smarthome.core.library.items import DateTimeItem as EclipseDateTimeItem
except:
    EclipseDateTimeType = None
    EclipseDateTimeItem = None

if 'org.eclipse.smarthome.automation' in sys.modules or 'org.openhab.core.automation' in sys.modules:
    # Workaround for Jython JSR223 bug where dates and datetimes are converted
    # to java.sql.Date and java.sql.Timestamp
    def remove_java_converter(clazz):
        if hasattr(clazz, '__tojava__'):
            del clazz.__tojava__
    remove_java_converter(datetime.date)
    remove_java_converter(datetime.datetime)


def format_date(value, format_string="yyyy-MM-dd'T'HH:mm:ss.SSxx"):
    # type: (t.Any, str) -> str
    """
    Returns string of ``value`` formatted according to ``format_string``.

    This function can be used when updating Items in openHAB or to format any
    date value for output. The default format string follows the same ISO8601
    format used in openHAB. If ``value`` does not have timezone information,
    the system default will be used.

    Examples:
        .. code-block::

            events.sendCommand("date_item", format_date(date_value))
            log.info("The time is currently: {}".format(format_date(ZonedDateTime.now())))

    Args:
        value: the value to convert
        format_string (str): the pattern to format ``value`` with.
            See `java.time.format.DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html>`_
            for format string tokens.

    Returns:
        str: the converted value
    """
    return str(to_java_zoneddatetime(value).format(DateTimeFormatter.ofPattern(format_string)))


def days_between(start_time, stop_time, calendar_days=False):
    # type: (t.Any, t.Any, bool) -> int
    """
    Returns the number of days between ``start_time`` and ``stop_time``.
    Will return a negative number if ``start_time`` is after ``stop_time``.

    Examples:
        .. code-block::

            span_days = days_between(items["date_item"], ZonedDateTime.now())

    Args:
        start_time: value to start from
        stop_time: value to measure to
        calendar_days (bool): if ``True``, the value returned will be the
            number of calendar days rather than 24-hour periods (default)

    Returns:
        int: the number of days between ``start_time`` and ``stop_time``
    """
    if calendar_days:
        return DAYS.between(to_java_zoneddatetime(start_time).toLocalDate().atStartOfDay(), to_java_zoneddatetime(stop_time).toLocalDate().atStartOfDay())
    else:
        return DAYS.between(to_java_zoneddatetime(start_time), to_java_zoneddatetime(stop_time))


def hours_between(start_time, stop_time):
    # type: (t.Any, t.Any) -> int
    """
    Returns the number of hours between ``start_time`` and ``stop_time``.
    Will return a negative number if ``start_time`` is after ``stop_time``.

    Examples:
        .. code-block::

            span_hours = hours_between(items["date_item"], ZonedDateTime.now())

    Args:
        start_time: value to start from
        stop_time: value to measure to

    Returns:
        int: the number of hours between ``start_time`` and ``stop_time``
    """
    return HOURS.between(to_java_zoneddatetime(start_time), to_java_zoneddatetime(stop_time))


def minutes_between(start_time, stop_time):
    # type: (t.Any, t.Any) -> int
    """
    Returns the number of minutes between ``start_time`` and ``stop_time``.
    Will return a negative number if ``start_time`` is after ``stop_time``.

    Examples:
        .. code-block::

            span_minutes = minutes_between(items["date_item"], ZonedDateTime.now())

    Args:
        start_time: value to start from
        stop_time: value to measure to

    Returns:
        int: the number of minutes between ``start_time`` and ``stop_time``
    """
    return MINUTES.between(to_java_zoneddatetime(start_time), to_java_zoneddatetime(stop_time))


def seconds_between(start_time, stop_time):
    # type: (t.Any, t.Any) -> int
    """
    Returns the number of seconds between ``start_time`` and ``stop_time``.
    Will return a negative number if ``start_time`` is after ``stop_time``.

    Examples:
        .. code-block::

            span_seconds = seconds_between(items["date_item"], ZonedDateTime.now())

    Args:
        start_time: value to start from
        stop_time: value to measure to

    Returns:
        int: the number of seconds between ``start_time`` and ``stop_time``
    """
    return SECONDS.between(to_java_zoneddatetime(start_time), to_java_zoneddatetime(stop_time))


def human_readable_seconds(seconds):
    # type: (int) -> str
    """
    Converts seconds into a human readable string of days, hours, minutes and
    seconds.

    Examples:
        .. code-block::

            message = human_readable_seconds(55555)
            # 15 hours, 25 minutes and 55 seconds

    Args:
        seconds: the number of seconds

    Returns:
        str: a string in the format ``{} days, {} hours, {} minutes and {}
        seconds``
    """
    seconds = int(round(seconds))
    number_of_days = seconds//86400
    number_of_hours = (seconds%86400)//3600
    number_of_minutes = (seconds%3600)//60
    number_of_seconds = (seconds%3600)%60

    days_string = "{} day{}".format(number_of_days, "s" if number_of_days > 1 else "")
    hours_string = "{} hour{}".format(number_of_hours, "s" if number_of_hours > 1 else "")
    minutes_string = "{} minute{}".format(number_of_minutes, "s" if number_of_minutes > 1 else "")
    seconds_string = "{} second{}".format(number_of_seconds, "s" if number_of_seconds > 1 else "")

    return "{}{}{}{}{}{}{}".format(
        days_string if number_of_days > 0 else "",
        "" if number_of_days == 0 or (number_of_hours == 0 and number_of_minutes == 0) else (
            " and " if (number_of_hours > 0 and number_of_minutes == 0 and number_of_seconds == 0) or (number_of_hours == 0 and number_of_minutes > 0 and number_of_seconds == 0) else ", "
        ),
        hours_string if number_of_hours > 0 else "",
        "" if number_of_hours == 0 or number_of_minutes == 0 else (
            " and " if number_of_minutes > 0 and number_of_seconds == 0 else ", "
        ),
        minutes_string if number_of_minutes > 0 else "",
        " and " if number_of_seconds > 0 and (number_of_minutes > 0 or number_of_hours > 0 or number_of_days > 0) else "",
        seconds_string if number_of_seconds > 0 else ""
    )


def to_java_zoneddatetime(value):
    # type: (t.Any) -> ZonedDateTime
    """
    Converts any of the supported date types to ``java.time.ZonedDateTime``. If
    ``value`` does not have timezone information, the system default will be
    used.

    Examples:
        .. code-block::

            java_time = to_java_zoneddatetime(items["date_item"])

    Args:
        value: the value to convert

    Returns:
        java.time.ZonedDateTime: the converted value

    Raises:
        TypeError: if the type of ``value`` is not supported by this module
    """
    if isinstance(value, ZonedDateTime):
        return value
    timezone_id = ZoneId.systemDefault()
    # java.time.LocalDateTime
    if isinstance(value, LocalDateTime):
        return value.atZone(timezone_id)
    # python datetime
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            timezone_id = ZoneId.ofOffset("GMT", ZoneOffset.ofTotalSeconds(int(value.utcoffset().total_seconds())))
        return ZonedDateTime.of(
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
    if isinstance(value, Calendar):
        return ZonedDateTime.ofInstant(value.toInstant(), ZoneId.of(value.getTimeZone().getID()))
    # java.util.Date
    if isinstance(value, Date):
        return ZonedDateTime.ofInstant(value.toInstant(), ZoneId.ofOffset("GMT", ZoneOffset.ofHours(0 - value.getTimezoneOffset() / 60)))
    # Joda DateTime
    if JodaDateTime and isinstance(value, JodaDateTime):
        return value.toGregorianCalendar().toZonedDateTime()
    # Eclipse Smarthome DateTimeType
    if EclipseDateTimeType and isinstance(value, EclipseDateTimeType):
        return to_java_zoneddatetime(value.calendar)
    # openHAB 2.x compat1x or OH3
    if DateTimeType and isinstance(value, DateTimeType):
        if hasattr(value,"calendar"):
            # compat1x
            return to_java_zoneddatetime(value.calendar)
        else:
            # OH3
            return value.getZonedDateTime()
    # Eclipse Smarthome DateTimeItem
    if EclipseDateTimeItem and isinstance(value, EclipseDateTimeItem):
        return to_java_zoneddatetime(value.getState())
    # openHAB DateTimeItem
    if DateTimeItem and isinstance(value, DateTimeItem):
        return to_java_zoneddatetime(value.getState())

    raise TypeError("Unknown type: {}".format(str(type(value))))


def to_python_datetime(value):
    # type: (t.Any) -> datetime.datetime
    """
    Converts any of the supported date types to Python ``datetime.datetime``.
    If ``value`` does not have timezone information, the system default will be
    used.

    Examples:
        .. code-block::

            python_time = to_python_datetime(items["date_item"])

    Args:
        value: the value to convert

    Returns:
        datetime.datetime: the converted value

    Raises:
        TypeError: if the type of ``value`` is not supported by this module
    """
    if isinstance(value, datetime.datetime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    return datetime.datetime(
        value_zoneddatetime.getYear(),
        value_zoneddatetime.getMonthValue(),
        value_zoneddatetime.getDayOfMonth(),
        value_zoneddatetime.getHour(),
        value_zoneddatetime.getMinute(),
        value_zoneddatetime.getSecond(),
        int(value_zoneddatetime.getNano() / 1000),
        _pythonTimezone(int(value_zoneddatetime.getOffset().getTotalSeconds() / 60))
    )


class _pythonTimezone(datetime.tzinfo):

    def __init__(self, offset=0, name=""):
        """
        Python tzinfo with ``offset`` in minutes and name ``name``.

        Args:
            offset (int): Timezone offset from UTC in minutes.
            name (str): Display name of this instance.
        """
        self.__offset = offset
        self.__name = name

    def utcoffset(self, value):
        return datetime.timedelta(minutes=self.__offset)

    def tzname(self, value):
        return self.__name

    def dst(self, value):
        return datetime.timedelta(0)


def to_joda_datetime(value):
    # type: (t.Any) -> JodaDateTime
    """
    Converts any of the supported date types to ``org.joda.time.DateTime``. If
    ``value`` does not have timezone information, the system default will be
    used.

    Examples:
        .. code-block::

            joda_time = to_joda_datetime(items["date_item"])

    Args:
        value: the value to convert

    Returns:
        org.joda.time.DateTime: the converted value
        None: if ``org.joda.time`` is not available

    Raises:
        TypeError: if the type of ``value`` is not suported by this package
    """
    if JodaDateTime is None:
        frame = inspect.stack()[1]
        getLogger("date").warn(
            "'{func}' ({file}:{line}) called 'to_joda_datetime' but Joda is not available"
            .format(file=frame.filename, line=frame.lineno, func=frame.function)
        )
        del frame
        return None

    if isinstance(value, JodaDateTime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    return JodaDateTime(value_zoneddatetime.toInstant().toEpochMilli(),
        JodaDateTimeZone.forTimeZone(TimeZone.getTimeZone(value_zoneddatetime.getZone()))
    )


def to_java_calendar(value):
    # type: (t.Any) -> Calendar
    """
    Converts any of the supported date types to ``java.util.Calendar``. If
    ``value`` does not have timezone information, the system default will be
    used.

    Examples:
        .. code-block::

            calendar_time = to_java_calendar(items["date_item"])

    Args:
        value: the value to convert

    Returns:
        java.util.Calendar: the converted value

    Raises:
        TypeError: if the type of ``value`` is not supported by this package
    """
    if isinstance(value, Calendar):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    new_calendar = Calendar.getInstance(TimeZone.getTimeZone(value_zoneddatetime.getZone().getId()))
    new_calendar.set(Calendar.YEAR, value_zoneddatetime.getYear())
    new_calendar.set(Calendar.MONTH, value_zoneddatetime.getMonthValue() - 1)
    new_calendar.set(Calendar.DAY_OF_MONTH, value_zoneddatetime.getDayOfMonth())
    new_calendar.set(Calendar.HOUR_OF_DAY, value_zoneddatetime.getHour())
    new_calendar.set(Calendar.MINUTE, value_zoneddatetime.getMinute())
    new_calendar.set(Calendar.SECOND, value_zoneddatetime.getSecond())
    new_calendar.set(Calendar.MILLISECOND, int(value_zoneddatetime.getNano() / 1000000))
    return new_calendar
