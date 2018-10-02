import esper.java
esper.java.initialize_log4j()

from datetime import datetime
from random import random

from java.util import Date, HashMap
from java.lang import String, Double

schema = {
    "time": Date,
    "symbol": String,
    "price": Double
}

#from java.lang import Thread
#print Thread.currentThread().getContextClassLoader()

from com.espertech.esper.client import EPServiceProviderManager, Configuration

print EPServiceProviderManager.classLoader

cfg = Configuration()
cfg.addEventType("StockTick", schema)
cep = EPServiceProviderManager.getProvider("engine", cfg)
runtime = cep.getEPRuntime()

def tick_generator():
    for i in xrange(10):
        tick = HashMap()
        tick.put("time", datetime.now())
        tick.put("price", 5.3 + random())
        tick.put("symbol", "AAPL")
        yield tick

admin = cep.getEPAdministrator()
statement = admin.createEPL("""
select * from
StockTick(symbol='AAPL').win:length(2)
having avg(price) < 6.0
""")

def event_listener(new_events, *args):
    print "event_listener", new_events[0].underlying

statement.addListener(event_listener)

for tick in tick_generator():
    runtime.sendEvent(tick, "StockTick")
