from inspect import isclass
from java.util import UUID
from org.eclipse.smarthome.automation import Rule as SmarthomeRule

from openhab.log import logging, log_traceback, LOG_PREFIX
from openhab.jsr223 import scope, get_automation_manager
scope.scriptExtension.importPreset("RuleSimple")

from org.slf4j import Logger, LoggerFactory

log = LoggerFactory.getLogger("org.eclipse.smarthome.automation.core.internal.RuleEngineImpl")

# this needs some attention in order to work with Automation API changes in 2.4.0 snapshots since build 1319
def set_uid_prefix(rule, prefix=None):
    if prefix is None:
        prefix = type(rule).__name__
    uid_field = type(SmarthomeRule).getClass(SmarthomeRule).getDeclaredField(SmarthomeRule, "uid")
    uid_field.setAccessible(True)
    uid_field.set(rule, "{}-{}".format(prefix, str(UUID.randomUUID())))

class _FunctionRule(scope.SimpleRule):
    def __init__(self, callback, triggers, name=None, tags=None):
        self.triggers = triggers
        self.callback = callback
        if name is None and hasattr(callback, '__name__'):
            name = callback.__name__
        self.name = name
        self.log = logging.getLogger(LOG_PREFIX + ("" if name is None else ("." + name)))
        if tags is not None:
            self.tags = set(tags)
        
    def execute(self, module, inputs):
        try:
            self.callback(inputs.get('event'))
        except:
            import traceback
            self.log.error(traceback.format_exc())

def rule(name=None, tags=None):
    try:
        if any(filter(lambda rule: rule.name == name, scope.rules.getAll())):
            raise ValueError("@rule: A rule already exists with the name \"{}\"".format(name))
        def rule_decorator(object):
            if isclass(object):
                clazz = object
                def init(self, *args, **kwargs):
                    scope.SimpleRule.__init__(self)
                    self.name = name or clazz.__name__
                    #set_uid_prefix(self)
                    self.log = logging.getLogger(LOG_PREFIX + "." + clazz.__name__)
                    clazz.__init__(self, *args, **kwargs)
                    if self.description is None and clazz.__doc__:
                        self.description = clazz.__doc__
                    self.triggers = log_traceback(self.getEventTriggers)()
                    if tags is not None:
                        self.tags = set(tags)
                subclass = type(clazz.__name__, (clazz, scope.SimpleRule), dict(__init__=init))
                subclass.execute = log_traceback(clazz.execute)
                return addRule(subclass())
            else:
                callable_obj = object
                simpleRule = _FunctionRule(callable_obj, callable_obj.triggers, name=name, tags=tags)
                newRule = get_automation_manager().addRule(simpleRule)
                callable_obj.UID = newRule.UID
                callable_obj.triggers = None
                return callable_obj
        return rule_decorator
    except Exception as e:
        import traceback
        log.error("@rule: Exception [{}]: [{}]".format(e, traceback.format_exc()))

def addRule(rule):
    get_automation_manager().addRule(rule)
