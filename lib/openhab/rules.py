from java.util import UUID
from org.eclipse.smarthome.automation import Rule as SmarthomeRule
from openhab.log import logging
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
    def __init__(self, *args, **kwargs):
      SimpleRule.__init__(self)
      set_uid_prefix(self)
      self.log = logging.getLogger("org.eclipse.smarthome.automation.rules." + type(self).__name__)
      clazz.__init__(self, *args, **kwargs)
      if hasattr(self, "getEventTriggers"):
          self.triggers = self.getEventTriggers()
      elif hasattr(self, "getEventTrigger"):
          self.triggers = self.getEventTrigger()

    return type(clazz.__name__, (clazz, SimpleRule), dict(__init__=__init__))
