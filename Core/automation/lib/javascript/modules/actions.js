'use strict';

//CommonJS
load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+'/automation/lib/javascript/personal/loader.js');


(function(context) {
    'use strict';
    
    var osgi = require('osgi');

    var oh1_actions = osgi.find_services("org.openhab.core.scriptengine.action.ActionService", null) || [];
    var oh2_actions = osgi.find_services("org.eclipse.smarthome.model.script.engine.action.ActionService", null) || [];

    oh1_actions.concat(oh2_actions).forEach(function (item, index) {
        context[item.actionClass.simpleName] = item.actionClass.static;
    });

    try {
        var Exec = Java.type('org.openhab.core.model.script.actions.Exec');
        var HTTP = Java.type('org.openhab.core.model.script.actions.HTTP');
        var LogAction = Java.type('org.openhab.core.model.script.actions.LogAction');
        var Ping = Java.type('org.openhab.core.model.script.actions.Ping');
        var ScriptExecution = Java.type('org.openhab.core.model.script.actions.ScriptExecution');
    } catch(e) {
        var Exec = Java.type('org.eclipse.smarthome.model.script.actions.Exec');
        var HTTP = Java.type('org.eclipse.smarthome.model.script.actions.HTTP');
        var LogAction = Java.type('org.eclipse.smarthome.model.script.actions.LogAction');
        var Ping = Java.type('org.eclipse.smarthome.model.script.actions.Ping');
        var ScriptExecution = Java.type('org.eclipse.smarthome.model.script.actions.ScriptExecution');
    }

    var static_imports = [Exec, HTTP, LogAction, Ping]

    static_imports.forEach(function (item, index) {
        context[item.class.simpleName] = item.class.static;
    });

})(exports);
