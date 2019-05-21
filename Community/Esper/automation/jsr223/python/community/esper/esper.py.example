from community import esper

from datetime import datetime
from random import random

from java.lang import String, Double, Object
from java.util import Date, HashMap

admin = esper.getEPAdministrator()
statement = admin.createEPL("""
    select name, avg(cast(state, float)) as average from
    ItemStateUpdate(name='TestString1').win:length(2)
    having avg(cast(state, float)) < 5.8
""")

def event_listener(new_events, *args):
    print "event_listener", new_events[0].underlying

statement.addListener(event_listener)

def tick_generator():
    now = 0
    previous_state = None
    for i in xrange(10):
        state = 5.3 + random()
        tick = HashMap()
        tick.put("time",  Date(now))
        tick.put("name", "TestString1")
        tick.put("previous_state", previous_state)
        tick.put("state", state)
        previous_state = state
        yield tick
        now += 1

runtime = esper.getEPRuntime()

print "START -------"
for tick in tick_generator():
    runtime.sendEvent(tick, "ItemStateUpdate")
print "END ---------"

statement.destroy()