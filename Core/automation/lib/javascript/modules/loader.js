var exports = {};
var module = {};

(function(context) {
    //'use strict';	

    var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");


context.require = function require(id) {
  if ( 'undefined' === typeof arguments.callee.require_stack ) { arguments.callee.require_stack = []; }
  var require_stack = arguments.callee.require_stack;
  if ( 'undefined' === typeof arguments.callee.modules ) { arguments.callee.modules = {}; }
  var modules = arguments.callee.modules;
  
  // if currently requiring module 'id', return partial exports
  if ( require_stack.indexOf(id) >= 0 ) {
    return modules[id].exports;
  }
  
  // if already required module 'id', return finished exports
  if ( modules[id] && modules[id].exports ) {
    return modules[id].exports;
  }
  
  // do the require of module 'id'
  // - if currently requiring a module, push global exports/module objects into arguments.callee.modules  
  if ( require_stack.length > 0 ) {
    var currently_requiring_id = require_stack[require_stack.length - 1];
    modules[currently_requiring_id] = {
      exports: exports,
      module: module
    };
  }
  
  //Java.type("org.slf4j.LoggerFactory").getLogger("loader").error("loading " + id);

  require_stack.push(id);
  exports = {};
  module = {};
  load(OPENHAB_CONF+'/automation/lib/javascript/modules/' + id + '.js');
  modules[id] = {
    exports: exports,
    module: module
  };
  require_stack.pop();
 
  //Java.type("org.slf4j.LoggerFactory").getLogger("loader").error("loaded " + JSON.stringify(exports));

  
  // restore last required modules' partial exports to the global space, or clear them
  if ( require_stack.length > 0 ) {
    var currently_requiring_id = require_stack[require_stack.length - 1];
    exports = modules[currently_requiring_id].exports;
    module = modules[currently_requiring_id].module;
  } else {
    exports = {};
    module = {};
  }
  
  // return arguments.callee.modules[id].exports;
  return arguments.callee.modules[id].exports;
}
})(this);