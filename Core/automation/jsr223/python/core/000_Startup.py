# pylint: disable=unused-import
"""
This is the first script to load and it will log system information to assist
with troubleshooting.
"""
from org.slf4j import LoggerFactory
LOG = LoggerFactory.getLogger("jython.startup")

from java.lang import System
import sys

try:
    import configuration
    configuration_py_installed = True
except:
    configuration_py_installed = False

LOG.warn("\n\n\
*******************************************************************************\n\
Jython version:             {}.{}.{}.{}\n\
Operating system:           {}\n\
OS Version:                 {}\n\
Java vendor:                {}\n\
Java VM name:               {}\n\
Java runtime name:          {}\n\
Java runtime version:       {}\n\
configuration.py installed: {}\n\
sys.path:                   {}\n\
*******************************************************************************\n".format(
sys.version_info[0], sys.version_info[1], sys.version_info[2], sys.version_info[3],
System.getProperty("os.name"),
System.getProperty("os.version"),
System.getProperty("java.vendor"),
System.getProperty("java.vm.name"),
System.getProperty("java.runtime.name"),
System.getProperty("java.runtime.version"),
str(configuration_py_installed),
"\n                            ".join(sys.path)))
