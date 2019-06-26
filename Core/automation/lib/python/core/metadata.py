"""
This module provides functions for manipulating Item Metadata.
"""

__all__ = [
    "get_all_namespaces", "get_metadata", "set_metadata", "remove_metadata",
    "get_value", "set_value", "get_key_value", "set_key_value",
    "remove_key_value"
]

from core import osgi
from core.jsr223.scope import itemRegistry

try:
    from org.openhab.core.items import Metadata, MetadataKey
except:
    from org.eclipse.smarthome.core.items import Metadata, MetadataKey

metadata_registry = osgi.get_service(
        "org.openhab.core.items.MetadataRegistry"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.items.MetadataRegistry"
    )

from core.log import logging, LOG_PREFIX
log = logging.getLogger("{}.core.metadata".format(LOG_PREFIX))

def get_all_namespaces(item_name):
    """
    This function will return a list of an Item's namespaces.

    Args:
        item_name (string): name of the Item to retrieve namespaces names from

    Returns:
        list of strings representing the namespace names found for the
            specified Item
    """
    log.debug("get_all_namespaces: Item [{}]".format(item_name))
    return map(lambda metadata: metadata.UID.namespace, filter(lambda metadata: metadata.UID.itemName == item_name, metadata_registry.getAll()))

def get_metadata(item_name, namespace):
    """
    This function will return the Metadata object associated with the
    specified Item.

    Args:
        item_name (string): name of the Item.
        namespace (string): name of the namespace.

    Returns:
        Metadata object: This will contain the namespace ``value`` and
            ``configuration`` dictionary
        None: metadata or Item does not exist
    """
    log.debug("get_metadata: Item [{}], namespace [{}]".format(item_name, namespace))
    return metadata_registry.get(MetadataKey(namespace, item_name))

def set_metadata(item_name, namespace, configuration, value=None, overwrite=False):
    """
    This function creates or modifies Item metadata, optionally overwriting
    the existing data. If not overwriting, the provided keys and values will
    be overlaid on top of the existing keys and values.

    Args:
        item_name (string): name of the Item
        namespace (string): name of the namespace
        configuration (dict): ``configuration`` dictionary to add to the
            namespace
        value (string): either the new namespace value or ``None``
        overwrite (bool): if ``True``, existing namespace data will be
            discarded
    """
    if overwrite:
        remove_metadata(item_name, namespace)
    metadata = get_metadata(item_name, namespace)
    if metadata is None or overwrite:
        log.debug("set_metadata: adding or overwriting metadata namespace with [value: {}, configuration: {}]: Item [{}], namespace [{}]".format(value, configuration, item_name, namespace))
        metadata_registry.add(Metadata(MetadataKey(namespace, item_name), value, configuration))
    else:
        if value is None:
            value = metadata.value
        new_configuration = dict(metadata.configuration).copy()
        new_configuration.update(configuration)
        log.debug("set_metadata: setting metadata namespace to [value: {}, configuration: {}]: Item [{}], namespace [{}]".format(value, new_configuration, item_name, namespace))
        metadata_registry.update(Metadata(MetadataKey(namespace, item_name), value, new_configuration))

def remove_metadata(item_name, namespace=None):
    """
    This function removes the Item metadata for the specified namepsace or for
    all namespaces.

    Args:
        item_name (string): name of the item
        namespace (string): name of the namespace or ``None``, which will
            remove metadata in all namespaces for the specified Item
    """
    if namespace is None:
        log.debug("remove_metadata (all): Item [{}]".format(item_name))
        metadata_registry.removeItemMetadata(item_name)
    else:
        log.debug("remove_metadata: Item [{}], namespace [{}]".format(item_name, namespace))
        metadata_registry.remove(MetadataKey(namespace, item_name))

def get_value(item_name, namespace):
    """
    This function will return the Item metadata ``value`` for the specified
    namespace.

    Args:
        item_name (string): name of the item
        namespace (string): name of the namespace

    Returns:
        value: namespace ``value``, can be ``None``
        None: metadata or Item does not exist
    """
    log.debug("get_value: Item [{}], namespace [{}]".format(item_name, namespace))
    metadata = get_metadata(item_name, namespace)
    if metadata is not None:
        return metadata.value
    else:
        return None

def set_value(item_name, namespace, value):
    """
    This function creates or updates the Item metadata ``value`` for the
    specified namespace.

    Args:
        item_name (string): name of the Item
        namespace (string): name of the namespace
        value (string): new or updated value for the namespace
    """
    log.debug("set_value: Item [{}], namespace [{}], value [{}]".format(item_name, namespace, value))
    metadata = get_metadata(item_name, namespace)
    if metadata is not None:
        set_metadata(item_name, namespace, metadata.configuration, value, True)
    else:
        set_metadata(item_name, namespace, {}, value)

def get_key_value(item_name, namespace, key):
    """
    Ths function returns the ``configuration`` value for the specified key.

    Args:
        item_name (string): name of the Item
        namespace (string): name of the namespace
        key (string): ``configuration`` key to return

    Returns:
        value: ``configuration`` key value, can be ``None``
        None: metadata or Item does not exist
    """
    log.debug("get_key_value: Item [{}], namespace [{}], key [{}]".format(item_name, namespace, key))
    metadata = get_metadata(item_name, namespace)
    if metadata is not None:
        return metadata.configuration.get(key)
    else:
        return None

def set_key_value(item_name, namespace, key, value):
    """
    This function creates or updates a ``configuration`` value in the
    specified namespace. This function cannot be used unless the namespace
    already exists.

    Args:
        item_name (string): name of the Item
        namespace (string): name of the namespace
        key (string): ``configuration`` key to create or update
        value (string or decimal): value to set for ``configuration`` key
    """
    log.debug("set_key_value: Item [{}], namespace [{}], key [{}], value [{}]".format(item_name, namespace, key, value))
    metadata = get_metadata(item_name, namespace)
    new_configuration = {key: value}
    if metadata is not None:
        new_configuration = dict(metadata.configuration).copy()
        new_configuration.update({key: value})
    set_metadata(item_name, namespace, new_configuration)

def remove_key_value(item_name, namespace, key):
    """
    This function removes a ``configuration`` key and its value from the
    specified namespace.

    Args:
        item_name (string): name of the Item
        namespace (string): name of the namespace
        key (string): ``configuration`` key to remove
    """
    log.debug("remove_key_value: Item [{}], namespace [{}], key [{}]".format(item_name, namespace, key))
    metadata = get_metadata(item_name, namespace)
    if metadata is not None:
        new_configuration = dict(metadata.configuration).copy()
        new_configuration.pop(key)
        set_metadata(item_name, namespace, new_configuration, metadata.value, True)
    else:
        log.debug("remove_key_value: metadata does not exist: Item [{}], namespace [{}]".format(item_name, namespace))
