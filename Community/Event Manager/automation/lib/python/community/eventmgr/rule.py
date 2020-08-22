import traceback 

from core.jsr223 import scope
from core.log import log_traceback
from core.actions import ScriptExecution
from core.triggers import ChannelEventTrigger, CronTrigger, ItemStateChangeTrigger, ItemStateUpdateTrigger
from community.eventmgr.base import EventBase

scope.scriptExtension.importPreset("RuleSupport")
scope.scriptExtension.importPreset("RuleSimple")

        
class EventHandlerRule(scope.SimpleRule, EventBase):
    """
    Internal Rule handler class for Event Manager events 
    """
    
    @log_traceback
    def __init__(self, eventmgr, ruleName = 'Event Manager - JSR223'):
        EventBase.__init__(self)        
        try:
            self._count = 0
            self.eventmgr = eventmgr
            self.triggers = []
            self.name = ruleName
            self.description = 'Subscription engine for events'
            self.tags = set('Event Subscription engine')
        except:
			self.Logger().error(traceback.format_exc())

    @log_traceback
    def execute(self, module, inputs):
        self.Logger().debug("[EventHandlerRule] module='{}', inputs='{}'".format(module, inputs))
        self.eventmgr.processEvent(module, inputs)
        
    @log_traceback    
    def addTrigger(self, objTrigger):
        try:
            self.triggers.append(objTrigger.trigger)
            self.Logger().debug("[addTrigger] Trigger='{}' Type='{}'".format(objTrigger, objTrigger.__class__.__name__))
        except:
			self.Logger().error(traceback.format_exc())
    
