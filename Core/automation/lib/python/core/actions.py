import sys
from core import osgi

__all__ = []

oh1_actions = osgi.find_services("org.openhab.core.scriptengine.action.ActionService", None) or []
oh2_actions = osgi.find_services("org.eclipse.smarthome.model.script.engine.action.ActionService", None) or []

_module = sys.modules[__name__]

for s in oh1_actions + oh2_actions:
    action_class = s.actionClass
    name = action_class.simpleName
    setattr(_module, name, action_class)
    __all__.append(name)

try:
    from org.openhab.core.model.script.actions import Exec
    from org.openhab.core.model.script.actions import HTTP
    from org.openhab.core.model.script.actions import LogAction
    from org.openhab.core.model.script.actions import Ping
except:
    from org.eclipse.smarthome.model.script.actions import Exec
    from org.eclipse.smarthome.model.script.actions import HTTP
    from org.eclipse.smarthome.model.script.actions import LogAction
    from org.eclipse.smarthome.model.script.actions import Ping

static_imports = [Exec, HTTP, LogAction, Ping]

for s in static_imports:
    name = s.simpleName
    setattr(_module, name, s)
    __all__.append(name)
