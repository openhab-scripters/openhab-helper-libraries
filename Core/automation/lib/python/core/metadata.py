"""
This module provides functions for manipulating Item Metadata.


"""

__all__ = [
    "get_all_namespaces", "get_metadata", "set_metadata", "remove_metadata",
    "get_value", "set_value", "get_key_value", "set_key_value",
    "remove_key_value"
]

from collections import MutableMapping
import re

from core import osgi
from core.jsr223.scope import itemRegistry
from core.utils import validate_item

try:
    from org.openhab.core.items import Metadata, MetadataKey
    from org.openhab.core.items import ItemNotFoundException
except:
    from org.eclipse.smarthome.core.items import Metadata, MetadataKey
    from org.eclipse.smarthome.core.items import ItemNotFoundException

metadata_registry = osgi.get_service(
        "org.openhab.core.items.MetadataRegistry"
    ) or osgi.get_service(
        "org.eclipse.smarthome.core.items.MetadataRegistry"
    )

from core.log import logging, LOG_PREFIX
log = logging.getLogger("{}.core.metadata".format(LOG_PREFIX))

# Valid characters for names
# this allows only numbers and letters for first char, 
# then numbers, letters, and underscore for the rest
_valid_chars_re = "^[a-zA-Z][a-zA-Z0-9_]*$"

def get_all_namespaces(item_name):
    """
    Lists all of an Item's namespaces.

    Args:
        item_name (string): Name of the item to scan.

    Returns:
        A list of strings representing the namespace names found for the
        item provided.

    Raises:
        ValueError: Iteam does not exist.
    """
    if validate_item(item_name) is None:
        raise ValueError("Item '{}' does not exist".format(item_name))
    return map(lambda metadata: metadata.UID.namespace, filter(lambda metadata: metadata.UID.itemName == item_name, metadata_registry.getAll()))

def get_metadata(item_name, namespace, muttable=False):
    """
    Gets a metadata object from the registry.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        muttable (bool): Set ``True`` to return a muttable ``configuration``
            in the metadata object, default is immutable.

    Returns:
        A metadata object containing the namespace ``value`` and
        ``configuration`` dictionary. Will return ``None`` if namespace does
        not exist.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    if validate_item(item_name) is None:
        raise ValueError("Item '{}' does not exist".format(item_name))
    if not re.match(_valid_chars_re, namespace):
        raise ValueError("'{}' is not a valid namespace name".format(namespace))
    log.debug("Fetching metadata namespace '{namespace}' from Item '{item}'".format(
        item=item_name, namespace=namespace))
    metadata = metadata_registry.get(MetadataKey(namespace, item_name))
    if muttable:
        metadata.configuratin = dict(metadata.configuratin).copy()
    log.debug("{metadata}".format(metadata=metadata))
    return metadata

def set_metadata(item_name, namespace, configuration, value=None, overwrite=False):
    """
    Sets metadata value and configuration.

    This function sets or updates a metadata namespace's value and
    configuration, optionally overwriting the existing data. If not overwriting,
    any existing keys with new values provided will be updated to the new
    values.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        configuration (dict): Configuration dict to add to namespace.
        value: New namespace value, ``None`` will use existing value.
        overwrite (bool): If ``True`` existing namespace data will be discarded.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    if validate_item(item_name) is None:
        raise ValueError("Item '{}' does not exist".format(item_name))
    if not re.match(_valid_chars_re, namespace):
        raise ValueError("'{}' is not a valid namespace name".format(namespace))
    log.debug("Saving metadata namespace '{namespace}' for Item '{item}'".format(
        item=item_name, namespace=namespace))
    if overwrite:
        remove_metadata(item_name, namespace)
    metadata = get_metadata(item_name, namespace)
    if metadata is None or overwrite:
        metadata_registry.add(Metadata(MetadataKey(namespace, item_name), value, configuration))
    else:
        if value is None:
            value = metadata.value
        new_configuration = dict(metadata.configuration).copy()
        new_configuration.update(configuration)
        metadata_registry.update(Metadata(MetadataKey(namespace, item_name), value, new_configuration))

def remove_metadata(item_name, namespace=None):
    """
    Removes metadata namespaces.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace, ``None`` will remove all
            namespaces for the specified item.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    if validate_item(item_name) is None:
        raise ValueError("Item '{}' does not exist".format(item_name))
    if namespace is None:
        log.debug("Deleting all metadata from Item '{item}'".format(item=item_name))
        metadata_registry.removeItemMetadata(item_name)
    else:
        if not re.match(_valid_chars_re, namespace):
            raise ValueError("'{}' is not a valid namespace name".format(namespace))
        log.debug("Deleting metadata namespace '{namespace}' from Item '{item}'".format(
            item=item_name, namespace=namespace))
        metadata_registry.remove(MetadataKey(namespace, item_name))

def get_value(item_name, namespace):
    """
    Returns the metadata value for the namespace.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    metadata = get_metadata(item_name, namespace)
    return metadata.value

def set_value(item_name, namespace, value):
    """
    Sets the metadata value for the namespace.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        value: New value for namespace.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    metadata = get_metadata(item_name, namespace)
    set_metadata(item_name, namespace, value, metadata.configuration)

def get_key_value(item_name, namespace, key):
    """
    Fetches the configuration value for the key provided.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        key (string): Key to fetch from the metadata configuration.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    metadata = get_metadata(item_name, namespace)
    return metadata.configuration.get(key)

def set_key_value(item_name, namespace, key, value):
    """
    Sets a metdata configuration value in the namespace.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        key (string): Configuration key to set.
        value: Value for configuration key.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    metadata = get_metadata(item_name, namespace)
    new_configuration = dict(metadata.configuration).copy()
    new_configuration.update({key: value})
    set_metadata(item_name, namespace, metadata.value, new_configuration)

def remove_key_value(item_name, namespace, key):
    """
    Removes a configuration key from the metadata namespace.

    Args:
        item_name (string): Name of the item.
        namespace (string): Name of the namespace.
        key (string): Configuration key to remove from the metadata.

    Raises:
        ValueError: Item does not exist.
        ValueError: Namespace name is invalid.
    """
    metadata = get_metadata(item_name, namespace)
    new_configuration = dict(metadata.configuration).copy()
    new_configuration.pop(key, None)
    set_metadata(item_name, namespace, metadata.value, new_configuration, True)
