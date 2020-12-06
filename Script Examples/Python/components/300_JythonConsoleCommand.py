"""
This script defines a Command extension to the OSGi console. The example
Command prints some Jython platform details to the console output.
"""
import platform

try:
    from org.openhab.core.io.console.extensions import AbstractConsoleCommandExtension
except:
    from org.eclipse.smarthome.io.console.extensions import AbstractConsoleCommandExtension

from core.osgi import register_service, unregister_service
from core.log import logging, LOG_PREFIX

LOG = logging.getLogger("{}.JythonConsoleCommand".format(LOG_PREFIX))

service = None


class JythonCommand(AbstractConsoleCommandExtension):
    def __init__(self):
        AbstractConsoleCommandExtension.__init__(self, "jython", "Jython command extension")

    def getUsages(self):
        return ["jython - (test) Jython interpreter information"]

    def execute(self, args, console):
        LOG.info('architecture:', platform.architecture()[0])
        LOG.info('java_ver:', platform.java_ver())
        LOG.info('node:', platform.node())
        LOG.info('processor:', platform.processor())
        LOG.info('python_compiler:', platform.python_compiler())
        LOG.info('python_implementation:', platform.python_implementation())
        LOG.info('python_version:', platform.python_version())
        LOG.info('release:', platform.release())


def scriptLoaded(id):
    global service
    service = JythonCommand()
    try:
        register_service(service, ["org.openhab.core.io.console.extensions.ConsoleCommandExtension"])
    except:
        register_service(service, ["org.eclipse.smarthome.io.console.extensions.ConsoleCommandExtension"])
    LOG.info("Registered command extension")


def scriptUnloaded():
    global service
    unregister_service(service)
