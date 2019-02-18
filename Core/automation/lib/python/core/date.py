"""
Date/time utilities for converting between the several different types used by openHAB.

Can convert the following types:
- java.time.ZonedDateTime
- java.time.LocalDateTime
- java.util.Calendar
- java.util.Date
- org.joda.DateTime
- datetime.datetime (Python)
- org.eclipse.smarthome.core.library.types.DateTimeType
- org.openhab.core.library.types.DateTimeType
"""
import datetime
import sys

if 'org.smarthome.automation' in sys.modules:
    # Workaround for Jython JSR223 bug where
    # dates and datetimes are converted to java.sql.Date
    # and java.sql.Timestamp
    def remove_java_converter(clazz):
        if hasattr(clazz, '__java__'):
            del clazz.__java__
    remove_java_converter(datetime.date)
    remove_java_converter(datetime.datetime)
    
from org.joda.time import DateTime, DateTimeZone
from java.util import Calendar, Date, TimeZone
from java.time import LocalDateTime, ZonedDateTime, ZoneId, ZoneOffset
from java.time.format import DateTimeFormatter
from java.time.temporal.ChronoUnit import DAYS, HOURS, MINUTES, SECONDS
from org.openhab.core.library.types import DateTimeType as LegacyDateTimeType
from org.eclipse.smarthome.core.library.types import DateTimeType

__all__ = ["formatDate", "daysBetween", "hoursBetween", "minutesBetween", "secondsBetween",
            "to_java_zoneddatetime", "toJTime", "to_java_calendar", "toJCal", 
            "to_python_datetime", "toPyDT", "pyTimezone",
            "to_joda_datetime", "toJodaDT"]


def formatDate(value, formatString="yyyy-MM-dd'T'HH:mm:ss.SSxx"):
    '''Returns string of date formatted according to formatString
    Accepts any date type used by this module'''
    return to_java_zoneddatetime(value).format(DateTimeFormatter.ofPattern(formatString))

def daysBetween(tFrom, tTo):
    '''Returns number of whole days between tFrom and tTo.
    Accepts any date type used by this module'''
    return DAYS.between(toJTime(tFrom), toJTime(tTo))

def hoursBetween(tFrom, tTo):
    '''Returns number of whole hours between tFrom and tTo.
    Accepts any date type used by this module'''
    return HOURS.between(toJTime(tFrom), toJTime(tTo))

def minutesBetween(tFrom, tTo):
    '''Returns number of whole minutes between tFrom and tTo.
    Accepts any date type used by this module'''
    return MINUTES.between(toJTime(tFrom), toJTime(tTo))

def secondsBetween(tFrom, tTo):
    '''Returns number of whole seconds between tFrom and tTo.
    Accepts any date type used by this module'''
    return SECONDS.between(toJTime(tFrom), toJTime(tTo))

def to_java_zoneddatetime(value):
    '''Returns java.time.ZonedDateTime (with system timezone if none specified)
    Accepts any date type used by this module'''
    TimezoneId = ZoneId.systemDefault()
    if isinstance(value, ZonedDateTime):
        return value
    # java.time.LocalDateTime
    if isinstance(value, LocalDateTime):
        return value.atZone(TimezoneId)
    # python datetime
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None: TimezoneId = ZoneId.ofOffset("GMT", ZoneOffset.ofTotalSeconds(value.utcoffset().total_seconds()))
        return ZonedDateTime.of(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond * 1000,
            TimezoneId
        )
    # java.util.Calendar
    if isinstance(value, Calendar):
        return ZonedDateTime.ofInstant(value.toInstant(), ZoneId.of(value.getTimeZone().getID()))
    # java.util.Date
    if isinstance(value, Date):
        return ZonedDateTime.ofInstant(value.toInstant(), ZoneId.ofOffset("GMT", ZoneOffset.ofTotalSeconds(value.getTimezoneOffset()*60)))
    # Joda DateTime
    if isinstance(value, DateTime):
        return value.toGregorianCalendar.toZonedDateTime
    # OH DateTimeType or ESH DateTimeType
    if isinstance(value, (LegacyDateTimeType, DateTimeType)):
        return to_java_zoneddatetime(value.calendar)

    raise Exception("Invalid conversion: " + str(type(value)))

def to_java_calendar(value):
    '''Returns java.util.calendar type
    Accepts any date type used by this module'''
    if isinstance(value, Calendar):
        return value
    
    zdt = to_java_zoneddatetime(value)
    c = Calendar.getInstance(TimeZone.getTimeZone(zdt.getZone().getID()))
    c.set(Calendar.YEAR, zdt.getYear)
    c.set(Calendar.MONTH, zdt.getMonthValue - 1)
    c.set(Calendar.DAY_OF_MONTH, zdt.getDayOfMonth)
    c.set(Calendar.HOUR_OF_DAY, zdt.getHour)
    c.set(Calendar.MINUTE, zdt.getMinute)
    c.set(Calendar.SECOND, zdt.getSecond)
    c.set(Calendar.MILLISECOND, int(zdt.getNano / 1000000))
    return c

def to_python_datetime(value):
    '''Returns Python datetime.datetime type
    Accepts any date type used by this module'''
    if isinstance(value, datetime.datetime):
        return value

    zdt = to_java_zoneddatetime(value)
    return datetime.datetime(
        zdt.getYear,
        zdt.getMonthValue,
        zdt.getDayOfMonth,
        zdt.getHour,
        zdt.getMinute,
        zdt.getSecond,
        int(zdt.getNano / 1000),
        pyTimezone(int(zdt.getOffset.getTotalSeconds / 60))
    )

def to_joda_datetime(value):
    '''Returns org.joda.time.DateTime type
    Accepts any date type used by this module'''
    if isinstance(value, DateTime):
            return value
    
    zdt = to_java_zoneddatetime(value)
    return DateTime(
        zdt.toInstant,
        DateTimeZone.forID(zdt.getZone().getID())
    )

class pyTimezone(datetime.tzinfo):
    '''Timezone with offset in minutes'''
    
    def __init__(self, offset=0, name=""):
        self.__offset = offset
        self.__name = name

    def utcoffset(self, dt):
        return datetime.timedelta(minutes = self.__offset)

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return datetime.timedelta(0)
    
    def offset_min(self):
        return int(self.__offset)

    def offset_milli(self):
        return int(self.__offset * 60 * 1000)

    def offset_hhmm(self):
        sHHMM = str(int(60 * (self.__offset % 60)))
        sHHMM = str(int(self.__offset / 60)) + sHHMM
        if len(sHHMM) < 4: sHHMM = "0" + sHHMM
        if self.__offset < 0:
            sHHMM = "-" + sHHMM
        else:
            sHHMM = "+" + sHHMM
        return sHHMM


# aliases
toJTime = to_java_zoneddatetime
toJCal = to_java_calendar
toPyDT = to_python_datetime
toJodaDT = to_joda_datetime
