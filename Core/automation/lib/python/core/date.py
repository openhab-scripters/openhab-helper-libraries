"""
This module provides functions for date and time conversions.

Types
=====

    It is recommended that you use ``java.time.ZonedDateTime`` for all
    operations involving dates or ``DateTime`` Items. See the documentation for
    `java.time.ZonedDateTime <https://docs.oracle.com/javase/8/docs/api/java/time/ZonedDateTime.html>`_
    for more information about its useage.

    The functions in this module can accept any of the following date types:

    .. code-block::

        java.time.ZonedDateTime
        java.time.LocalDateTime
        java.util.Calendar
        java.util.Date
        org.joda.time.DateTime
        datetime.datetime (Python)
        org.eclipse.smarthome.core.library.types.DateTimeType
        org.openhab.core.library.types.DateTimeType
        DateTimeFormatter.ISO_ZONED_DATE_TIME (String)

Functions
=========
"""

import re, sys
import time, datetime

if 'org.eclipse.smarthome.automation' in sys.modules or 'org.openhab.core.automation' in sys.modules:
    # Workaround for Jython JSR223 bug where dates and datetimes are converted
    # to java.sql.Date and java.sql.Timestamp
    def remove_java_converter(clazz):
        if hasattr(clazz, '__tojava__'):
            del clazz.__tojava__
    remove_java_converter(datetime.date)
    remove_java_converter(datetime.datetime)

from java.time import LocalDateTime, ZonedDateTime
from java.time import ZoneId, ZoneOffset
from java.time.format import DateTimeFormatter
from java.time.temporal.ChronoUnit import DAYS, HOURS, MINUTES, SECONDS
from org.joda.time import DateTime, DateTimeZone
from java.util import Calendar, Date, TimeZone
from org.eclipse.smarthome.core.library.types import DateTimeType as eclipseDateTime

try:
    # if the compat1x bundle is not installed, the OH 1.x DateTimeType is not available
    from org.openhab.core.library.types import DateTimeType as legacyDateTime
except:
    legacyDateTime = None

__all__ = [
    "format_date",
    "days_between", "hours_between", "minutes_between", "seconds_between",
    "to_java_zoneddatetime", "to_java_calendar", "to_python_datetime",
    "to_joda_datetime", "millis", "joda_now", "elapsed"
]


def format_date(value, format_string="yyyy-MM-dd'T'HH:mm:ss.SSxx"):
    """
    Returns string of ``value`` formatted according to ``format_string``.

    This function can be used when updating Items in openHAB or to format any
    date value for output. The default format string follows the same ISO8601
    format used in openHAB.

    Examples:
        .. code-block::

            sendCommand("date_item", format_date(date_value))
            log.info("The time is currently: {}".format(format_date(ZonedDateTime.now())))

    Arguments:
        value: Any supported date value
        format_string (str): Pattern to format ``value`` with.
            See `java.time.format.DateTimeFormatter <https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html>`_
            for format string tokens.

    Returns:
        A string representation of ``value`` according to ``format_string``.
        If ``value`` does not have timezone information, the system default
        will be used.
    """
    return to_java_zoneddatetime(value).format(DateTimeFormatter.ofPattern(format_string))

def days_between(value_from, value_to, calendar_days=False):
    """
    Returns the number of days between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_days = days_between(items["date_item"], ZonedDateTime.now())

    Arguments:
        value_from: Value to start from
        value_to: Value to measure to
        calendar_days (bool): If ``True``, the value returned will be the
            number of calendar days rather than 24-hour periods (default).
    """
    if calendar_days:
        return DAYS.between(to_java_zoneddatetime(value_from).toLocalDate().atStartOfDay(), to_java_zoneddatetime(value_to).toLocalDate().atStartOfDay())
    else:
        return DAYS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def hours_between(value_from, value_to):
    """
    Returns the number of hours between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_hours = hours_between(items["date_item"], ZonedDateTime.now())

    Arguments:
        value_from: Value to start from
        value_to: Value to measure to
    """
    return HOURS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def minutes_between(value_from, value_to):
    """
    Returns the number of minutes between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_minutes = minutes_between(items["date_item"], ZonedDateTime.now())

    Arguments:
        value_from: Value to start from
        value_to: Value to measure to
    """
    return MINUTES.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def seconds_between(value_from, value_to):
    """
    Returns the number of seconds between ``value_from`` and ``value_to``.
    Will return a negative number if ``value_from`` is after ``value__to``.

    Examples:
        .. code-block::

            span_seconds = seconds_between(items["date_item"], ZonedDateTime.now())

    Arguments:
        value_from: Value to start from
        value_to: Value to measure to
    """
    return SECONDS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def to_java_zoneddatetime(value):
    """
    Converts any of the supported date types to ``java.time.ZonedDateTime``.

    Examples:
        .. code-block::

            java_time = to_java_zoneddatetime(items["date_item"])

    Arguments:
        value: Any supported date value

    Returns:
        A ``java.time.ZonedDateTime`` representing ``value``. If ``value``
        does not have timezone information, the system default will be used.

    Raises:
        DateTimeParseException: If ``value`` is a string and can't be parsed
        TypeError: If the type of ``value`` is not supported by this module
    """
    # org.joda.time.DateTime String
    if isinstance(value, basestring):
        return ZonedDateTime.parse(value)
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
    if isinstance(value, DateTime):
        return value.toGregorianCalendar().toZonedDateTime()
    # openHAB DateTimeType
    if isinstance(value, eclipseDateTime):
        return to_java_zoneddatetime(value.calendar)
    # openHAB 1.x DateTimeType
    if legacyDateTime and isinstance(value, legacyDateTime):
        return to_java_zoneddatetime(value.calendar)

    raise TypeError("Unknown type: {}".format(str(type(value))))

def to_python_datetime(value):
    """
    Converts any of the supported date types to Python ``datetime.datetime``.

    Examples:
        .. code-block::

            python_time = to_python_datetime(items["date_item"])

    Arguments:
        value: Any supported date value

    Returns:
        A Python ``datetime.datetime`` representing ``value``. If ``value``
        does not have timezone information, the system default will be used.

    Raises:
        TypeError: If the type of ``value`` is not supported by this module
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

        Arguments:
            offset (int): Timezone offset from UTC in minutes.
            name (str): Display name of this instance.
        """
        self.__offset = offset
        self.__name = name

    def utcoffset(self, value):
        return datetime.timedelta(minutes = self.__offset)

    def tzname(self, value):
        return self.__name

    def dst(self, value):
        return datetime.timedelta(0)

def to_joda_datetime(value):
    """
    Converts any of the supported date types to ``org.joda.time.DateTime``.

    Examples:
        .. code-block::

            joda_time = to_joda_datetime(items["date_item"])

    Arguments:
        value: Any supported date value

    Returns:
        | An ``org.joda.time.DateTime`` representing ``value``.
        | If ``value`` does not have timezone information, the system default
          will be used.

    Raises:
        TypeError: If type of ``value`` is not suported by this package.
    """
    if isinstance(value, DateTime):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    value_zoneId = value_zoneddatetime.getZone().getId().replace('GMT','')
    return DateTime(
        value_zoneddatetime.toInstant().toEpochMilli(),
        DateTimeZone.forID(value_zoneId)
    )

def to_java_calendar(value):
    """
    Converts any of the supported date types to ``java.util.Calendar``.

    Examples:
        .. code-block::

            calendar_time = to_java_calendar(items["date_item"])

    Arguments:
        value: Any supported date value

    Returns:
        A ``java.util.Calendar`` representing ``value``. If ``value`` does not
        have timezone information, the system default will be used.

    Raises:
        TypeError: If type of ``value`` is not supported by this package.
    """
    if isinstance(value, Calendar):
        return value

    value_zoneddatetime = to_java_zoneddatetime(value)
    value_zoneId = value_zoneddatetime.getZone().getId()
    if re.match(r"[-+][0-2][\d]:[0-5][\d]", value_zoneId): # Match to '+HH:MM'
        value_zoneId = 'GMT' + value_zoneId                # Convert to 'GMT+HH:MM'
    new_calendar = Calendar.getInstance(TimeZone.getTimeZone(value_zoneId))
    new_calendar.set(Calendar.YEAR, value_zoneddatetime.getYear())
    new_calendar.set(Calendar.MONTH, value_zoneddatetime.getMonthValue() - 1)
    new_calendar.set(Calendar.DAY_OF_MONTH, value_zoneddatetime.getDayOfMonth())
    new_calendar.set(Calendar.HOUR_OF_DAY, value_zoneddatetime.getHour())
    new_calendar.set(Calendar.MINUTE, value_zoneddatetime.getMinute())
    new_calendar.set(Calendar.SECOND, value_zoneddatetime.getSecond())
    new_calendar.set(Calendar.MILLISECOND, int(value_zoneddatetime.getNano() / 1000000))
    return new_calendar

def human_readable_seconds(seconds):
    """
    Converts seconds into a human readable string of days, hours, minutes and seconds.

    Examples:
        .. code-block::

            message = human_readable_seconds(55555)
            # 15 hours, 25 minutes and 55 seconds

    Arguments:
        seconds: The number of seconds

    Returns:
        string: A string in the format ``{} days, {} hours, {} minutes and {} seconds``
    """
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


def millis():
    """
    Get the current time in millis (unix epoch) as an int to 
    simplify generic timing applications
    
    Arguments:
        none
    
    Returns: 
        int: current time in millis since unix epoch
    """
    return int(round(time.time() * 1000))

def joda_now(string=False):
    """
    Get the Joda DateTime object or Joda DateTime
    string to be used in updating OpenHAB DateTime items
    
    Arguments:
        string: Boolean, defaults to False
    
    Returns:
        DateTime: If 'string' == False, returns a Joda DateTime object
        string: If 'string' == True, returns string representation of 
                Joda DateTime ('2019-09-03T15:22:33.650+05:00')
    
    Code Block:
        from core.date import joda_now
        
        events.postUpdate("SomeDateTimeItem", joda_now(True))
    """
    if string == True:
        return str(to_joda_datetime(ZonedDateTime.now()))
    else: 
        return to_joda_datetime(ZonedDateTime.now())

def elapsed(start, end=joda_now(), format='digital'):
    """
    Arguments:
        start:  Start time in any datetime type or joda zdtt string (Required)
        end:    End time, optional. If not included the current time will be used
        format: 'digital' - Returns string '(-)HH:MM:SS' or '(-)Dd HH:MM:SS' [DEFAULT]
                'text'    - Returns human readable string '2 days, 3 hours and 45 minutes'
                'seconds' - Returns the seconds as a float (with ms precision)
    
    Returns:
        (see args)

    Code Block:
        from core.date import elapsed, joda_now
        
        example.log.info("Elapsed: {}".format(elapsed(items.SomeDateTimeItem)))  
        example.log.info("Elapsed: {}".format(elapsed(items.SomeDateTimeItem, joda_now(True), format='text')))  
        example.log.info("Elapsed: {}".format(elapsed(items.SomeDateTimeItem, joda_now(), format='seconds')))  
        
        Output:
        Elapsed: 405d 13:37:17
        Elapsed: 405 days, 13 hours and 37 minutes
        Elapsed: 35041036.273
    """
    e_digital = '00:00:00'      
    e_text    = '0 seconds'
    e_seconds = 0.0

    start_pdt = to_python_datetime(start)
    end_pdt = to_python_datetime(end)
    td = (end_pdt - start_pdt)          # Total time delay (as timedelta)

    ts = e_seconds = td.total_seconds() # Retains ms precision (total seconds)
    sign = '-' if (ts < 0) else ''      # Get the sign of 'ts'          
    ts = int(abs(ts))                   # Make 'ts' a positive integer

    days, seconds = divmod(ts, 86400)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    seconds = int(round(float(seconds) + (float(td.microseconds) / 1000.0 / 1000.0)))
    
    # Format the digital elapsed output
    if days > 0:
        e_digital = "{}{}d {:02d}:{:02d}:{:02d}".format(sign, days, hours, minutes, seconds)
    else:
        e_digital = "{}{:02d}:{:02d}:{:02d}".format(sign, hours, minutes, seconds)

    # Format the human readable elapsed output
    e_text = human_readable_seconds(ts)
    if sign == '-': e_text = "Negative " + e_text

    if   format == 'seconds':   return e_seconds # Retains ms precision
    elif format == 'text':      return e_text
    else:                       return e_digital
