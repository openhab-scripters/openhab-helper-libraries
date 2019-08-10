/*
This library provides functions for getting, registering, unregistering, and
finding OSGi services.
*/

'use strict';

(function(context) {
    'use strict';

    var FrameworkUtil = Java.type("org.osgi.framework.FrameworkUtil");

    var _bundle = FrameworkUtil.getBundle(scriptExtension.class);
    var bundle_context = (_bundle !== null) ? _bundle.getBundleContext() : null;
    var registered_services = [];

    context.get_service = function(class_or_name) {
        if (bundle_context !== null) {
            var classname = (typeof class_or_name === "object") ? class_or_name.getName() : class_or_name;
            var ref = bundle_context.getServiceReference(classname);
            return (ref !== null) ? bundle_context.getService(ref) : null;
        }
    }

    context.find_services = function(class_name, filter) {
        if (bundle_context !== null) {
            var refs = bundle_context.getAllServiceReferences(class_name, filter);
            if (refs !== null) {
                var services = [];
                for (var i = 0, size = refs.length; i < size ; i++) {
                    services.push(bundle_context.getService(refs[i]));
                }
                return services;
            }
        }
    }

    context.register_service = function(service, interface_names, properties) {
        if (properties !== null) {
            var util = Java.type("java.util");
            p = util.Hashtable();
            for (var i = 0, size = properties.length; i < size ; i++) {
                p.put(k, v);
            }
            properties = p;
        }
        else {
            properties = null;
        }
        var reg = bundle_context.registerService(interface_names, service, properties);
        for (var i = 0, size = interface_names.length; i < size ; i++) {
            registered_services[name] = (service, reg);
        }
        return reg;
    }

    context.unregister_service = function(service) {
        var keys = registered_services.keys();
        for (var i = 0, size = keys.length; i < size ; i++) {
            var registered_service, reg = registered_services[key];
            if (service == registered_service) {
                registered_services.splice(i, keys[i]);
                reg.unregister();
            }
        }
    }

})(this);
