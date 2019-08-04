"""
REST Based Metadata Editor - Metadata
"""

import json
from ast import literal_eval
from rest_utils import rest_get, rest_put, rest_delete


def get_metadata(item_name, namespace, host):
    """Fetches metadata namespace for item.

    Returns ``{}`` if item or namespace don't exist.
    """
    def parse(data):
        for key in data:
            try:
                data[key] = json.loads(data[key])
                parse(data[key])
            except:
                try:
                    data[key] = literal_eval(str(data[key]))
                    parse(data[key])
                except:
                    pass

    resp = rest_get(host, "items/{item}".format(item=item_name), "metadata={namespace}".format(namespace=namespace))
    if resp:
        resp_json = json.loads(resp.text)
        metadata = resp_json.get("metadata", {}).get(namespace, {})
        parse(metadata)
        return metadata
    else:
        return {}

def set_metadata(item_name, namespace, host, configuration, value=None, overwrite=False):
    """
    This function creates or modifies Item metadata, optionally overwriting
    the existing data. If not overwriting, the provided keys and values will
    be overlaid on top of the existing keys and values.
    Examples:
        .. code-block::
            # Add/change metadata in an Item's namespace (only overwrites existing keys and "value" is optional)
            set_metadata("Item_Name", "Namespace_Name", {"Key_1": "key 1 value", "Key_2": 2, "Key_3": False}, "namespace_value")
            # Overwrite metadata in an Item's namespace with new data
            set_metadata("Item_Name", "Namespace_Name", {"Key_5": 5}, overwrite=True)
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
        remove_metadata(item_name, namespace, host) # may not need for REST
    metadata = get_metadata(item_name, namespace, host)
    if not metadata or overwrite:
        #log.debug("set_metadata: adding or overwriting metadata namespace with [value: {}, configuration: {}]: Item [{}], namespace [{}]".format(value, configuration, item_name, namespace))
        resp = rest_put(
                host,
                "items/{item_name}/metadata/{namespace}".format(item_name=item_name, namespace=namespace),
                {"value": value, "config": configuration}
            )
        if resp:
            return True if resp.status_code in [200, 201] else False
        else:
            return False
    else:
        if value is None:
            value = metadata.get("value", None)
        new_configuration = metadata.get("config", {})
        new_configuration.update(configuration)
        #log.debug("set_metadata: setting metadata namespace to [value: {}, configuration: {}]: Item [{}], namespace [{}]".format(value, new_configuration, item_name, namespace))
        resp = rest_put(
                host,
                "items/{item_name}/metadata/{namespace}".format(item_name=item_name, namespace=namespace),
                {"value": value, "config": new_configuration}
            )
        if resp:
            return True if resp.status_code in [200, 201] else False
        else:
            return False

def remove_metadata(item_name, namespace, host):
    if namespace is not None:
        resp = rest_delete(host, "items/{item_name}/metadata/{namespace}".format(item_name=item_name, namespace=namespace))
        if resp:
            return True if resp.status_code == 200 else False
        else:
            return False

def get_value(item_name, namespace, host):
    """Fetches metadata namespace value for item.

    Returns ``None`` if item or namespace don't exist.
    """
    metadata = get_metadata(item_name, namespace, host)
    return metadata.get("value", None)