from inspect import isclass
from java.util import UUID
from org.eclipse.smarthome.automation import Rule as SmarthomeRule

from core.log import logging, LOG_PREFIX, log_traceback
from core.jsr223 import scope, get_automation_manager

scope.scriptExtension.importPreset("RuleSimple")

# this needs some attention in order to work with Automation API changes in 2.4.0 snapshots since build 1319
def set_uid_prefix(rule, prefix=None):
    if prefix is None:
        prefix = type(rule).__name__
    uid_field = type(SmarthomeRule).getClass(SmarthomeRule).getDeclaredField(SmarthomeRule, "uid")
    uid_field.setAccessible(True)
    uid_field.set(rule, "{}-{}".format(prefix, str(UUID.randomUUID())))

class _FunctionRule(scope.SimpleRule):
    def __init__(self, callback, triggers, name=None, description=None, tags=None):
        self.triggers = triggers
        self.callback = callback
        if name is None:
            if hasattr(callback, '__name__'):
                name = callback.__name__
            else:
                name = "JSR223-Jython"
        self.name = name or callback.__name__
        self.log = logging.getLogger(LOG_PREFIX + ("" if name is None else ("." + name)))
        if description is not None:
            self.description = description
        if tags is not None:
            self.tags = set(tags)
        
    def execute(self, module, inputs):
        try:
            self.callback(inputs.get('event'))
        except:
            import traceback
            self.log.error(traceback.format_exc())

def rule(name=None, description=None, tags=None):
    def rule_decorator(object):
        if isclass(object):
            clazz = object
            def init(self, *args, **kwargs):
                scope.SimpleRule.__init__(self)
                if name is None:
                    if hasattr(clazz, '__name__'):
                        self.name = clazz.__name__
                    else:
                        self.name = "JSR223-Jython"
                else:
                    self.name = name
                #set_uid_prefix(self)
                self.log = logging.getLogger(LOG_PREFIX + "." + clazz.__name__)
                clazz.__init__(self, *args, **kwargs)
                if description is not None:
                    self.description = description
                elif self.description is None and clazz.__doc__:
                    self.description = clazz.__doc__
                if hasattr(self, "getEventTriggers"):
                    self.triggers = log_traceback(self.getEventTriggers)()
                if tags is not None:
                    self.tags = set(tags)
            subclass = type(clazz.__name__, (clazz, scope.SimpleRule), dict(__init__=init))
            subclass.execute = log_traceback(clazz.execute)
            return addRule(subclass())
        else:
            function = object
            newRule = _FunctionRule(function, function.triggers, name=name, description=description, tags=tags)
            get_automation_manager().addRule(newRule)
            function.triggers = None
            return function
    return rule_decorator

def addRule(rule):
    get_automation_manager().addRule(rule)