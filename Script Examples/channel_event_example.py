from core.triggers import ChannelEventTrigger
from core.rules import rule, addRule

@rule
class channelEventExample(object):

    def get_event_triggers(self):
        return [ChannelEventTrigger('astro:sun:away:set#event','START','Sunset_Away')]
                    
    def execute(self,modules,inputs):
        self.log.info('Sunset triggered')

addRule(channelEventExample())
      
