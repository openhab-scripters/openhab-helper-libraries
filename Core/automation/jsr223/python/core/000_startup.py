from org.slf4j import LoggerFactory
LOG = LoggerFactory.getLogger("jython.Startup")

from java.lang import System
import sys, platform

LOG.warn("")
if hasattr(sys.version_info, "major"):
    LOG.warn("Jython version: {}.{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro, sys.version_info.releaselevel))
else:
    LOG.warn("Jython version: {}".format(sys.version))
LOG.warn("Operating system: {}".format(System.getProperty("os.name")))
LOG.warn("OS Version: {}".format(System.getProperty("os.version")))
LOG.warn("Architecture: {}".format(platform.uname()[5]))
LOG.warn("Java version: {}".format(sys.platform))
LOG.warn("sys.path: {}".format(sys.path))
LOG.warn("")
