import json

import community.esper.java

import core
from core.osgi.events import OsgiEventAdmin
from core.log import logging, LOG_PREFIX

log = logging.getLogger(LOG_PREFIX + ".esper")

from java.lang import String, Double, Object
from java.util import Date

from com.espertech.esper.client import EPServiceProviderManager, Configuration

item_state_schema = {
    "type": String,
    "time": Date,
    "name": String,
    "state": Object
}

item_state_changed_schema = {
    "type": String,
    "time": Date,
    "name": String,
    "previous_state": Object,
    "state": Object
}

item_command_schema = {
    "type": String,
    "time": Date,
    "name": String,
    "command": Object,
}

channel_event_schema = {
    "type": String,
    "time": Date,
    "name": String,
    "command": Object,
}

def esper_bridge(event):
    event_type = event.getProperty('type')
    if event_type == 'ItemStateEvent':
        event_payload = json.loads(event.getProperty('payload'))
        event_topic = event.getProperty('topic').split('/')
        item_name = event_topic[2]
        record = {
            "type": event_type,
            "time": Date(),
            "name": item_name,
            "state": event_payload['value']
        }
        runtime.sendEvent(record, record['type'])
    elif event_type == 'ItemStateChangedEvent':
        event_payload = json.loads(event.getProperty('payload'))
        event_topic = event.getProperty('topic').split('/')
        item_name = event_topic[2]
        record = {
            "type": event_type,
            "time": Date(),
            "name": item_name,
            "previous_state": event_payload['oldValue'],
            "state": event_payload['value']
        }
        runtime.sendEvent(record, record['type'])
    elif event_type == 'ItemCommandEvent':
        event_payload = json.loads(event.getProperty('payload'))
        event_topic = event.getProperty('topic').split('/')
        item_name = event_topic[2]
        record = {
            "type": event_type,
            "time": Date(),
            "name": item_name,
            "command": event_payload['value'],
        }
        runtime.sendEvent(record, record['type'])

runtime = None

def scriptLoaded(*args):
    global runtime
    configuration = Configuration()
    configuration.addEventType("ItemStateEvent", item_state_schema)
    configuration.addEventType("ItemStateChangedEvent", item_state_schema)
    configuration.addEventType("ItemCommandEvent", item_command_schema)
    configuration.addEventType("ChannelEvent", channel_event_schema)
    core.esper = EPServiceProviderManager.getProvider("engine", configuration)
    runtime = core.esper.getEPRuntime()
    log.info("Created Esper provider")
    OsgiEventAdmin.add_listener(esper_bridge)
    log.info("Esper event bridge registered")

def scriptUnloaded():
    if hasattr(core, "esper") and core.esper:
        core.esper.destroy()
        core.esper = None
        log.info("Destroyed Esper provider")
        OsgiEventAdmin.remove_listener(esper_bridge)
        log.info("Esper event bridge removed")

        

