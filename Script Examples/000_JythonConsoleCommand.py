import platform

from openhab.log import logging
from openhab.osgi import register_service, unregister_service
from org.eclipse.smarthome.io.console.extensions import AbstractConsoleCommandExtension

class JythonCommand(AbstractConsoleCommandExtension):
    def __init__(self):
        AbstractConsoleCommandExtension.__init__(self, "jython", "Example Jython command extension")
    
    def getUsages(self):
        return ["jython - (test) Jython interpreter informationb"]

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
    logging.info("Registered command extension")

def scriptUnloaded():
    global service
    unregister_service(service)
