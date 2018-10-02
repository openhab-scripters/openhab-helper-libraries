"""
Date/time utilities for converting between the several different types
used by openHAB.
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
    
from org.joda.time import DateTime
from java.util import Calendar, Date
from java.text import SimpleDateFormat
from java.time import LocalDateTime
from org.openhab.core.library.types import DateTimeType as LegacyDateTimeType
from org.eclipse.smarthome.core.library.types import DateTimeType

date_formatter = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")

def to_java_calendar(value):
    if isinstance(value, Calendar):
        return value
    
    if isinstance(value, datetime.datetime):
        c = Calendar.getInstance()
        c.set(Calendar.YEAR, value.year)
        c.set(Calendar.MONTH, value.month - 1)
        c.set(Calendar.DAY_OF_MONTH, value.day)
        c.set(Calendar.HOUR_OF_DAY, value.hour)
        c.set(Calendar.MINUTE, value.minute)
        c.set(Calendar.SECOND, value.second)
        c.set(Calendar.MILLISECOND, value.microsecond / 1000)
        return c

    if isinstance(value, Date):
        c = Calendar.getInstance()
        c.time = value
        return c
    
    if isinstance(value, DateTime):
        return value.toGregorianCalendar()
       
    if isinstance(value, LegacyDateTimeType):
        return value.calendar
 
    if isinstance(value, DateTimeType):
        return value.calendar

    raise Exception("Invalid conversion: " + str(type(value)))

def to_python_datetime(value):
    if isinstance(value, datetime.datetime):
        return value

    calendar = to_java_calendar(value)

    return datetime.datetime(
        calendar.get(Calendar.YEAR),
        calendar.get(Calendar.MONTH) + 1,
        calendar.get(Calendar.DAY_OF_MONTH),
        calendar.get(Calendar.HOUR_OF_DAY),
        calendar.get(Calendar.MINUTE),
        calendar.get(Calendar.SECOND),
        calendar.get(Calendar.MILLISECOND) * 1000,
    )

    raise Exception("Invalid conversion: " + str(type(value)))

def to_joda_datetime(value):
    if isinstance(value, DateTime):
            return value
            
    calendar = to_java_calendar(value)
    
    return DateTime(
        calendar.get(Calendar.YEAR),
        calendar.get(Calendar.MONTH) + 1,
        calendar.get(Calendar.DAY_OF_MONTH),
        calendar.get(Calendar.HOUR_OF_DAY),
        calendar.get(Calendar.MINUTE),
        calendar.get(Calendar.SECOND),
        calendar.get(Calendar.MILLISECOND),
    )
