from openhab.triggers import ChannelEventTrigger
from openhab.rules import rule, addRule

@rule
class channelEventExample(object):

    def get_event_triggers(self):
        return [ChannelEventTrigger('astro:sun:away:set#event','START','Sunset_Away') ])
                    
    def execute(self,modules,inputs):
        self.log.info('Sunset triggered')

addRule(channelEventExample())
      
