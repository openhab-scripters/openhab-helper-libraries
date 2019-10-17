var exports = {};
var module = {};

(function (context) {
  'use strict';

  var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");

  //(Java)Log - don't depend on standard logging as it depends on the init system
  var jLog = Java.type("org.slf4j.LoggerFactory").getLogger("jsr223.javascript.init")

  var init_state;

  //start init loader
  if (typeof ___INIT_STATE___ === 'undefined') {
    jLog.debug("Created init runtime")
    init_state = {
      require_stack: [],
      loaded_modules: {}
    };
    context.___INIT_STATE___ = init_state;

  } else {
    init_state = ___INIT_STATE___;
  }

  //end init loader

  var scriptTemplate = function (id, dir) {
    return 'load("' + OPENHAB_CONF + '/automation/lib/javascript/' + dir + "/" + id + '.js");';
  };

  var stackString = function (stack, optionalCurrent) {
    var rv = stack.join(">");
    if (typeof optionalCurrent != 'undefined') {
      if (stack.length > 0) {
        rv += ">";
      }
      rv += optionalCurrent;
    }
    return "[" + rv + "]";
  }

  var doLoad = function (id) {

    try { //allow personal to override modules
      load({
        script: scriptTemplate(id, "personal"),
        name: 'personal-loader'
      });
      jLog.debug(stackString(init_state.require_stack) + "loaded personal script " + id);
    } catch (e) {
      if (e.toString().startsWith("javax.script.ScriptException: TypeError: Cannot load script from")) { //script not there; warn only
        jLog.debug(stackString(init_state.require_stack) + "No script named " + id + " in personal; falling back to core");
      } else {
        jLog.error(stackString(init_state.require_stack) + "Error loading " + id + ": " + e);
      }
      load({
        script: scriptTemplate(id, "core"),
        name: 'core-loader'
      });
      jLog.debug(stackString(init_state.require_stack) + "loaded core script " + id);
    }

    jLog.debug(stackString(init_state.require_stack) + "retrieved exports:  " + Object.keys(exports));
  };

  context.require = function require(id) {
    jLog.debug("modules: " + Object.keys(init_state.loaded_modules));

    jLog.debug(stackString(init_state.require_stack, id) + "Attempting to retreive module " + id);

    // if currently requiring module 'id', return partial exports
    if (init_state.require_stack.indexOf(id) >= 0) {
      jLog.debug(stackString(init_state.require_stack, id) + "Currently requiring module " + require_stack[require_stack.length - 1] + ", returning partial exports");
      return init_state.loaded_modules[id].exports;
    }

    // if already required module 'id', return finished exports
    if (init_state.loaded_modules[id] && init_state.loaded_modules[id].exports) {
      jLog.debug(stackString(init_state.require_stack, id) + "Module already loaded; returning cached version");
      return init_state.loaded_modules[id].exports;
    }

    // do the require of module 'id'
    // - if currently requiring a module, push global exports/module objects into arguments.callee.modules  
    if (init_state.require_stack.length > 0) {
      var currently_requiring_id = init_state.require_stack[init_state.require_stack.length - 1];
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