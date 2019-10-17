var exports = {};
var module = {};

(function (context) {
  'use strict';	

  var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");

  var buildEngine = function (){
    var ScriptEngineManager = Java.type('javax.script.ScriptEngineManager');
    var factory = new ScriptEngineManager();
    return factory.getEngineByName("JS");
  };

  var engine = buildEngine();

  //(Java)Log - don't depend on standard logging as it depends on the init system
  var jLog = Java.type("org.slf4j.LoggerFactory").getLogger("jsr223.javascript.init")

  var init_state = (function(){
    if (typeof ___INIT_STATE___  === 'undefined') {
      jLog.debug("Created init runtime")
      return {
        require_stack: [],
        loaded_modules: {}
      };
    } else {
      return ___INIT_STATE___;
    }
  })();

  
  var newContext = function (engine) {
    var SimpleScriptContext = Java.type('javax.script.SimpleScriptContext');
    var ScriptContext = Java.type('javax.script.ScriptContext');

    var ctx = new SimpleScriptContext();
    ctx.setBindings(engine.createBindings(), ScriptContext.ENGINE_SCOPE);
    ctx.setAttribute("scriptExtension", scriptExtension, ScriptContext.ENGINE_SCOPE);
    ctx.setAttribute("exports", exports, ScriptContext.ENGINE_SCOPE);
    ctx.setAttribute("module", module, ScriptContext.ENGINE_SCOPE);
    ctx.setAttribute("___INIT_STATE___", init_state, ScriptContext.ENGINE_SCOPE);

    return ctx;
  };

  var scriptTemplate = function (id, dir) {
    return  'load(Java.type("java.lang.System").getenv("OPENHAB_CONF")+"/automation/lib/javascript/core/init.js");\n' +
            'load("' + OPENHAB_CONF + '/automation/lib/javascript/' + dir + "/" + id + '.js");';
  };

  var doLoad = function(id) {
    var ctx = newContext(engine);

    try { //allow personal to override modules
      engine.eval(scriptTemplate(id, "personal"), ctx);
      jLog.debug("loaded personal script " + id);
    } catch (e) {
      if (e.toString().startsWith("javax.script.ScriptException: TypeError: Cannot load script from")) { //script not there; warn only
        jLog.debug("No script named " + id + " in personal; falling back to core");
      } else {
        jLog.error("Error loading " + id + ": " + e);
      }
      engine.eval(scriptTemplate(id, "core"), ctx);
      jLog.debug("loaded core script " + id);
    }

    exports = ctx.getAttribute("exports");
    jLog.debug("retrieved exports:  " + Object.keys(exports));
  };

  context.require = function require(id) {

    jLog.debug("Attempting to retreive module " + id);

    // if currently requiring module 'id', return partial exports
    if (init_state.require_stack.indexOf(id) >= 0) {
      jLog.debug("Currently requiring module " + require_stack[require_stack.length-1] + ", returning partial exports");
      return init_state.loaded_modules[id].exports;
    }

    // if already required module 'id', return finished exports
    if (init_state.loaded_modules[id] && init_state.loaded_modules[id].exports) {
      jLog.debug("Module already loaded; returning cached version");
      return init_state.loaded_modules[id].exports;
    }

    // do the require of module 'id'
    // - if currently requiring a module, push global exports/module objects into arguments.callee.modules  
    if (init_state.require_stack.length > 0) {
      var currently_requiring_id = init_state.require_stack[require_stack.length - 1];
      init_state.loaded_modules[currently_requiring_id] = {
        exports: exports,
        module: module
      };
    }

    init_state.require_stack.push(id);

    doLoad(id);

    init_state.loaded_modules[id] = {
      exports: exports,
      module: module
    };
    init_state.require_stack.pop();

    // restore last required modules' partial exports to the global space, or clear them
    if (init_state.require_stack.length > 0) {
      var currently_requiring_id = init_state.require_stack[init_state.require_stack.length - 1];
      exports = init_state.loaded_modules[currently_requiring_id].exports;
      module = init_state.loaded_modules[currently_requiring_id].module;
    } else {
      exports = {};
      module = {};
    }

    return init_state.loaded_modules[id].exports;
  }
})(this);