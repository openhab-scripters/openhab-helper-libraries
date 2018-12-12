from random import random

schema = {
    "time": Date,
    "symbol": String,
    "price": Double
}

from java.io import File
from com.espertech.esper.client import EPServiceProviderManager, Configuration

cfg = Configuration()
cfg.addEventType("StockTick", schema)
cep = EPServiceProviderManager.getProvider("engine", cfg)
runtime = cep.getEPRuntime()

admin = cep.getEPAdministrator()
module = admin.deploymentAdmin.read(File("example3.epl"))
admin.deploymentAdmin.deploy(module, None)

def dump_event(new_events, old_events, *args):
    def fmt_events(e):
        return e is None and "None" or str(map(lambda e: e.underdlying, e))
    print "{} dumpe_event:\n  new: {}\n  old: {}\n  args: {}".format(
        now, fmt_events(new_events), fmt_events(old_events), args[0].name)

# ----------------
# Simulation

from java.util import HashMap
from datetime import timedelta
from random import random
from com.espertech.esper.client.time import CurrentTimeEvent

now - timedelta()

def event_generator():
    global now
     for i in xrange(100):
         runtime.sendEvent(CurrentTimeEvent(int(now.total_seconds() * 1000)))
         evt = HashMap()
         evt.put("time", int(now.total_seconds() * 1000))
         evt.put("item", "TestItem")
         evt.put("state", "ON")
         yield evt, "UpdateEvent"
         now += timedelta(seconds=random * 0.4)

for evt in event_generator():
    runtime.sendEvent(*evt)