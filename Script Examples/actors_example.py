import re
import collections
import json
import pykka
import threading

from core.osgi.events import OsgiEventAdmin, log_event, event_dict
from org.osgi.framework import Filter

from core.log import logging, LOG_PREFIX
openhab_log = logging.getLogger(LOG_PREFIX + ".ActorExample")

from org.python.modules.sre import PatternObject

pykka.ActorRegistry.stop_all()

class LogActor(pykka.ThreadingActor):
    def __init__(self):
        pykka.ThreadingActor.__init__(self)
        
    def on_receive(self, message):
        openhab_log.info(message.get('message'))
  
logger_ref = LogActor.start()

def log(fmt, *args):
    logger_ref.tell({'message': fmt.format(*args)})
      
class OpenhabDispatcher(pykka.ThreadingActor):
    def __init__(self):
        pykka.ThreadingActor.__init__(self)
        self._subscriptions = collections.defaultdict(list)
        
    def subscribe(self, subscriber, filter):
        self._subscriptions[filter].append(subscriber)
    
    def unsubscribe(self, subscriber, filter=None):
        if filter:
            self._subscriptions[filter].remove(subscriber)
        else:
            for subs in self._subscriptions.values():
                subs.remove(subscriber)
        
    def on_receive(self, message):
        log('on_receive {}'.format(message))
        if message.get('message_type') == 'osgi_event':
            for filter in self._subscriptions:
                log('  filter {}'.format(filter))
                if filter.matchCase(message):
                    for s in self._subscriptions[filter]:
                        log('  dispatch to {}'.format(s))
                        s.tell(message)

dispatcher_ref = OpenhabDispatcher.start()
OpenhabDispatcher.INSTANCE = dispatcher_ref.proxy()

class DictFilter(Filter):
    def __init__(self, properties):
        self._properties = properties

    def matchCase(self, d):
        for key, value in self._properties.iteritems():
            other_value = d.get(key)
            log('     match {} {} {} {}'.format(key, value, other_value, bool(value == other_value)))
            if isinstance(value, PatternObject):
                if not value.match(other_value):
                    return False
            elif value != other_value:
                return False
        return True
       
    def __repr__(self):
        return "{}${}".format(type(self).__name__, self._properties)
    
class ItemEventFilter(DictFilter):
    def __init__(self, item_name, topic_suffix):
        properties = {'type': type(self).__name__.replace("Filter", "")}
        if item_name:
            properties['topic'] = "smarthome/items/{}/{}".format(item_name, topic_suffix)
        DictFilter.__init__(self, properties)
    
class ItemStateEventFilter(ItemEventFilter):
    def __init__(self, item_name=None):
        ItemEventFilter.__init__(self, item_name, "state")

class ItemStateChangedEventFilter(ItemEventFilter):
    def __init__(self, item_name=None):
        ItemEventFilter.__init__(self, item_name, "statechanged")

class ItemCommandEventFilter(ItemEventFilter):
    def __init__(self, item_name=None):
        ItemEventFilter.__init__(self, item_name, "command")
                
class EchoActor(pykka.ThreadingActor):
    def __init__(self, input_item_name, output_item_name):
        pykka.ThreadingActor.__init__(self)
        self.output_item_name = output_item_name
        filter = ItemStateChangedEventFilter(input_item_name)
        OpenhabDispatcher.INSTANCE.subscribe(self.actor_ref, filter)
        
    def on_receive(self, message):
        log("EchoActor {} {}".foirmat(id(self), message))
        payload = json.loads(message.get('payload'))
        value = payload.get('value')
        events.postUpdate(self.output_item_name, value)
    
echo_actor = EchoActor.start("EchoInput", "EchoOutput")

previous_event = None

def handle_event(e):
    global previous_event
    log_event(e)
    if e != previous_event and e.topic == 'smarthome' and not e.getProperty('bridgemarker'):
        d = event_dict(e)
        d['message_type'] = 'osgi_event'
        dispatcher_ref.tell(d)
        previous_event = e

def scriptLoaded(*args):
    try:
        OsgiEventAdmin.add_listener(handle_event)
    except:
        import traceback
        print traceback.format_exc()
 
def scriptUnloaded():
    OsgiEventAdmin.remove_listener(handle_event)