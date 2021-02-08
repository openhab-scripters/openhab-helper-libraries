# pylint: disable=unused-import

try:
    from org.openhab.core.model.script.actions import Exec
    from org.openhab.core.model.script.actions import HTTP
    from org.openhab.core.model.script.actions import Ping
    from org.openhab.core.model.script.actions import ScriptExecution
except:
    from org.eclipse.smarthome.model.script.actions import Exec
    from org.eclipse.smarthome.model.script.actions import HTTP
    from org.eclipse.smarthome.model.script.actions import Ping
    from org.eclipse.smarthome.model.script.actions import ScriptExecution

try:
    # OH3
    from org.openhab.core.model.script.actions import Log
    LogAction = Log
except:
    try:
        # OH2 post ESH merge
        from org.openhab.core.model.script.actions import LogAction
        Log = LogAction
    except:
        # OH2 pre ESH merge
        from org.eclipse.smarthome.model.script.actions import LogAction
        Log = LogAction
