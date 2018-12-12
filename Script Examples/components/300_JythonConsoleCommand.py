import platform

from core.osgi import register_service, unregister_service
from org.eclipse.smarthome.io.console.extensions import AbstractConsoleCommandExtension
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".jythonConsoleCommand")

class JythonCommand(AbstractConsoleCommandExtension):
    def __init__(self):
        AbstractConsoleCommandExtension.__init__(self, "jython", "Example Jython command extension")
    
    def getUsages(self):
        return ["jython - (test) Jython interpreter information"]

    def execute(self, args, console):
        print 'architecture:', platform.architecture()[0]
        print 'java_ver:', platform.java_ver()
        print 'node:', platform.node()
        print 'processor:', platform.processor()
        print 'python_compiler:', platform.python_compiler()
        print 'python_implementation:', platform.python_implementation()
        print 'python_version:', platform.python_version()
        print 'release:', platform.release()
        
def scriptLoaded(id):
    global service
    service = JythonCommand()
    interfaces = ["org.eclipse.smarthome.io.console.extensions.ConsoleCommandExtension"]
    registration = register_service(service, interfaces)
    log.info("Registered command extension")

def scriptUnloaded():
    global service
    unregister_service(service)