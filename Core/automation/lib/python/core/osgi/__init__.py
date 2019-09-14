"""
Provides utility functions for retrieving, registering and removing OSGi
services.
"""
__all__ = [
    'get_service',
    'find_services',
    'register_service',
    'unregister_service'
]

from core.jsr223.scope import scriptExtension
from org.osgi.framework import FrameworkUtil

_bundle = FrameworkUtil.getBundle(type(scriptExtension))
bundle_context = _bundle.getBundleContext() if _bundle else None

registered_services = {}

def get_service(class_or_name):
    """
    This function gets the specified OSGi service.

    Args:
        class_or_name (class or str): the class or class name of the service to
            get

    Returns:
        OSGi service or None: the requested OSGi service or None
    """
    if bundle_context:
        classname = class_or_name.getName() if isinstance(class_or_name, type) else class_or_name
        ref = bundle_context.getServiceReference(classname)
        return bundle_context.getService(ref) if ref else None
    else:
        return None

def find_services(class_name, filter):
    """
    This function finds the specified OSGi service.

    Args:
        class_or_name (class or str): the class or class name of the service to
            get
        filter (str): the filter expression or None for all services

    Returns:
        list: a list of matching OSGi services
    """
    if bundle_context:
        refs = bundle_context.getAllServiceReferences(class_name, filter)
        if refs:
            return [bundle_context.getService(ref) for ref in refs]
    else:
        return None

def register_service(service, interface_names, properties=None):
    """
    This function registers the specified service object with the specified
    properties under the specified class names into the Framework.

    Args:
        service (java.lang.Object): the service to register
        interface_names (list): a list of class names
        properties (dict): a dict of properties for the service

    Returns:
        ServiceRegistration: a ServiceRegistration object used to update or
        unregister the service
    """
    if properties:
        import java.util
        p = java.util.Hashtable()
        for k, v in properties.iteritems():
            p.put(k, v)
        properties = p
    reg = bundle_context.registerService(interface_names, service, properties)
    for name in interface_names:
        registered_services[name] = (service, reg)
    return reg

def unregister_service(service):
    """
    This function unregisters an OSGi service.

    Args:
        service (java.lang.Object): the service to unregister
    """
    keys = registered_services.keys()
    for key in keys:
        registered_service, reg = registered_services[key]
        if service == registered_service:
            del registered_services[key]
            reg.unregister()
