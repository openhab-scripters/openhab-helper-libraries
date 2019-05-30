"""
Date/time utilities for converting between the several different types used by openHAB.

This module can convert to the following types:
- java.time.ZonedDateTime (prefered)    to_java_zoneddatetime
- java.util.Calendar                    to_java_calendar
- org.joda.DateTime                     to_joda_datetime
- datetime.datetime                     to_python_datetime
and can convert from the following types:
- java.time.ZonedDateTime
- java.time.LocalDateTime
- java.util.Calendar
- java.util.Date
- org.joda.DateTime
- datetime.datetime (Python)
- org.eclipse.smarthome.core.library.types.DateTimeType
- org.openhab.core.library.types.DateTimeType

It can also format any of these types for sending to an openHAB Item using
format_date(value), which will return the date as a string in the correct format.

There are also some conveniece functions for determining the span between two datetimes.
days_between, hours_between, minutes_between, and seconds_between will return the
number of whole units of each unit of time between the two datetimes passed. They
will return negative numbers if the first datetime passed is after the second.
See docs for java.time.temporal.ChronoUnit, if you want more information.
"""
import datetime
import sys

if 'org.eclipse.smarthome.automation' in sys.modules or 'org.openhab.core.automation' in sys.modules:
    # Workaround for Jython JSR223 bug where dates and datetimes are converted
    # to java.sql.Date and java.sql.Timestamp
    def remove_java_converter(clazz):
        if hasattr(clazz, '__tojava__'):
            del clazz.__tojava__
    remove_java_converter(datetime.date)
    remove_java_converter(datetime.datetime)
    
from org.joda.time import DateTime, DateTimeZone
from java.util import Calendar, Date, TimeZone
from java.time import LocalDateTime, ZonedDateTime, ZoneId, ZoneOffset
from java.time.format import DateTimeFormatter
from java.time.temporal.ChronoUnit import DAYS, HOURS, MINUTES, SECONDS
from org.openhab.core.library.types import DateTimeType as LegacyDateTimeType
from org.eclipse.smarthome.core.library.types import DateTimeType

__all__ = ["ZonedDateTime", "format_date", 
           "days_between", "hours_between", "minutes_between", "seconds_between",
           "to_java_zoneddatetime", "toJTime", "to_java_calendar", "toJCal", 
           "to_python_datetime", "toPyDT", "pythonTimezone",
           "to_joda_datetime", "toJodaDT"]


def format_date(value, format_string="yyyy-MM-dd'T'HH:mm:ss.SSxx"):
    '''Returns string of date formatted according to format_string.
    Accepts any date type used by this module.
    See java.time.format.DateTimeFormatter docs for format string tokens.'''
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
    '''Returns number of whole hours between value_from and value_to. 
    Accepts any date type used by this module'''
    return HOURS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def minutes_between(value_from, value_to):
    '''Returns number of whole minutes between value_from and value_to. 
    Accepts any date type used by this module.'''
    return MINUTES.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def seconds_between(value_from, value_to):
    '''Returns number of whole seconds between value_from and value_to. 
    Accepts any date type used by this module.'''
    return SECONDS.between(to_java_zoneddatetime(value_from), to_java_zoneddatetime(value_to))

def to_java_zoneddatetime(value):
    '''Returns java.time.ZonedDateTime (with system timezone, if none specified). 
    Accepts any date type used by this module.'''
    timezone_id = ZoneId.systemDefault()
    if isinstance(value, ZonedDateTime):
        return value
    # java.time.LocalDateTime
    if isinstance(value, LocalDateTime):
        return value.atZone(timezone_id)
    # python datetime
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None: timezone_id = ZoneId.ofOffset("GMT", ZoneOffset.ofTotalSeconds(value.utcoffset().total_seconds()))
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
        return ZonedDateTime.ofInstant(value.toInstant(), ZoneId.ofOffset("GMT", ZoneOffset.ofTotalSeconds(value.getTimezoneOffset()*60)))
    # Joda DateTime
    if isinstance(value, DateTime):
        return value.toGregorianCalendar().toZonedDateTime()
    # OH DateTimeType or ESH DateTimeType
    if isinstance(value, (LegacyDateTimeType, DateTimeType)):
        return to_java_zoneddatetime(value.calendar)

    raise Exception("Invalid conversion: " + str(type(value)))

def to_java_calendar(value):
    '''Returns java.util.calendar type (with system timezone if none specified). 
    Accepts any date type used by this module'''
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

def to_python_datetime(value):
    '''Returns Python datetime.datetime type (with system timezone if none specified). 
    Accepts any date type used by this module'''
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
        pythonTimezone(int(value_zoneddatetime.getOffset().getTotalSeconds() / 60))
    )

def to_joda_datetime(value):
    '''Returns org.joda.time.DateTime type (with system timezone if none specified). 
    Accepts any date type used by this module'''
    if isinstance(value, DateTime):
            return value
    
    value_zoneddatetime = to_java_zoneddatetime(value)
    return DateTime(
        value_zoneddatetime.toInstant(),
        DateTimeZone.forID(value_zoneddatetime.getZone().getId())
    )

class pythonTimezone(datetime.tzinfo):
    '''Python tzinfo with offset in minutes.'''
    
    def __init__(self, offset=0, name=""):
        self.__offset = offset
        self.__name = name

    def utcoffset(self, value):
        return datetime.timedelta(minutes = self.__offset)

    def tzname(self, value):
        return self.__name

    def dst(self, value):
        return datetime.timedelta(0)

# aliases
toJTime = to_java_zoneddatetime
toJCal = to_java_calendar
toPyDT = to_python_datetime
toJodaDT = to_joda_datetime
