'use strict';

var FrameworkUtil = Java.type("org.osgi.framework.FrameworkUtil");

var _bundle = FrameworkUtil.getBundle(scriptExtension.class);
var bundle_context = (typeof _bundle !== "undefined") ? _bundle.getBundleContext() : null;
var registered_services = [];

function get_service(class_or_name) {
    if (typeof bundle_context !== "undefined") {
        var classname = (typeof class_or_name === "object") ? class_or_name.getName() : class_or_name;
        var ref = bundle_context.getServiceReference(classname);
        return (typeof ref !== "undefined") ? bundle_context.getService(ref) : null;
    }
}

function find_services(class_name, filter) {
    if (typeof bundle_context !== "undefined") {
        var refs = bundle_context.getAllServiceReferences(class_name, filter);
        if (typeof refs !== "undefined") {
            var services = [];
            for (var i = 0, size = refs.length; i < size ; i++) {
                services.push(bundle_context.getService(refs[i]));
            }
            return services;
        }
    }
}

function register_service(service, interface_names, properties) {
    if (typeof properties !== "undefined") {
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

function unregister_service(service) {
    var keys = registered_services.keys();
    for (var i = 0, size = keys.length; i < size ; i++) {
        var registered_service, reg = registered_services[key];
        if (service == registered_service) {
            registered_services.splice(i, keys[i]);
            reg.unregister();
        }
    }
}
