import sys
import os

__all__ = []

_base = os.path.dirname(__file__)

ESPER_LIBS = [
    os.path.join(_base, "esper-6.1.0.jar"),
    #os.path.join(_base, "log4j-1.2.17.jar"),
    #os.path.join(_base, "slf4j-api-1.7.21.jar"),
    #os.path.join(_base, "slf4j-log4j12-1.7.21.jar"),
    os.path.join(_base, "antlr-runtime-4.5.3.jar"),
    os.path.join(_base, "cglib-nodep-3.2.4.jar")
]

for lib in ESPER_LIBS:
    print lib
    sys.path.append(lib)

def initialize_log4j():
    try:
        from org.apache.log4j import (
            ConsoleAppender, Level, Logger, PatternLayout
        )
        rootLogger = Logger.getRootLogger()
        print dir(rootLogger)
        rootLogger.level = Level.DEBUG
        layout = PatternLayout("%d{ISO8601} [%t] %-5p %c %x - %m%n")
        appender = ConsoleAppender(layout)
        rootLogger.addAppender(appender)
    except:
        import traceback
        print traceback.format_exc()

from java.lang import Thread, ClassLoader
from java.net import URLClassLoader, URL

esperClassLoader = URLClassLoader(
    [URL("file:"+lib) for lib in ESPER_LIBS],
    ClassLoader.getSystemClassLoader())

