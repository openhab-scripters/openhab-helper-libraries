""""
This script just forces a reload of the modules which causes
trigger types to be registered. This operation can and will 
be made more explicit later.

This script causes the following trigger types to be defined:
    jsr223.StartupTrigger
    jsr223.OsgiEventTrigger

Once defined, these trigger types can be viewed and used in the
OSGI console, the Paper UI, the ReST API and so on.
"""

import openhab.triggers
reload(openhab.triggers)

import openhab.osgi.events
reload(openhab.osgi.events)

