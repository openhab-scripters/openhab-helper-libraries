from java.util import UUID
from org.eclipse.smarthome.automation import Rule as SmarthomeRule

from openhab.log import logging, log_traceback, LOG_PREFIX
from openhab.jsr223.scope import scriptExtension

scriptExtension.importPreset("RuleSimple")
scriptExtension.importPreset("RuleSupport")
from openhab.jsr223.scope import SimpleRule, automationManager

def set_uid_prefix(rule, prefix=None):
    if prefix is None:
        prefix = type(rule).__name__
    uid_field = type(SmarthomeRule).getClass(SmarthomeRule).getDeclaredField(SmarthomeRule, "uid")
    uid_field.setAccessible(True)
    uid_field.set(rule, "{}-{}".format(prefix, str(UUID.randomUUID())))
    
def rule(clazz):
    def init(self, *args, **kwargs):
        SimpleRule.__init__(self)
        set_uid_prefix(self)
        self.log = logging.getLogger(LOG_PREFIX + "." + clazz.__name__)
        clazz.__init__(self, *args, **kwargs)
        if hasattr(self, "getEventTriggers"):
            self.triggers = log_traceback(self.getEventTriggers)()
        elif hasattr(self, "getEventTrigger"):
            # For OH1 compatibility
            self.triggers = log_traceback(self.getEventTrigger)()
    subclass = type(clazz.__name__, (clazz, SimpleRule), dict(__init__=init))
    subclass.execute = log_traceback(clazz.execute)
    return subclass
