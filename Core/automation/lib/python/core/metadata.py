'''
Wrapper class for using Item Metadata
'''

from collections import MutableMapping
from org.eclipse.smarthome.core.items import Metadata, MetadataKey
from core.log import logging, LOG_PREFIX
log = logging.getLogger(LOG_PREFIX + ".metadata")
from core import osgi
MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

__all__ = [ "namespace_exists", "item_metadata", "metadata_namespace" ]


def namespace_exists(item_name, namespace):
    '''Returns True if metadata namespace exists'''
    return False if MetadataRegistry.get(MetadataKey(namespace, item_name)) is None else True

def _resolveType(value):
    '''Attempts to resolve the type of the metadata value.
    It will return the value as the python type if possible,
    otherwise will return value as string'''
    if str(value).lower().strip() == "true":
        return True
    elif str(value).lower().strip() == "false":
        return False
    else:
        # attempt to cast to int
        try: return int(str(value))
        except ValueError: pass
        # attempt to cast to float
        try: return float(str(value))
        except ValueError: pass
        # not a number
        return str(value)

class item_metadata(MutableMapping):
    def __init__(self, item_name):
        '''This is a manager class that can be used to manage multiple
        metadata namespaces for a single item from one place.
        - This class behaves like a dict of "metadata_namespace" objects.
        - Namespaces can be added by name with "add_namespace(name)"
        (attempting to add a namespace that already exists will raise a KeyError)'''
        self._item_name = item_name
        self._namespaces = {}

    def __iter__(self): return iter(self._namespaces)
    def __len__(self): return len(self._namespaces)
    def __setitem__(self, key, value): raise AttributeError("Direct assignment to keys not possible")
    def __getitem__(self, key): return self._namespaces[key]
    def __delitem__(self, key): self.delete_namespace(key)

    def add_namespace(self, name):
        '''Creates a new namespace instance and loads it from the registry
        if it exists.'''
        if name in self._namespaces: raise KeyError
        else: self._namespaces[name] = metadata_namespace(self._item_name ,name)

    def delete_namespace(self, name, remove=False):
        '''Deletes the specified namespace from this object. It will not
        remove the namespace from openHAB unless the "remove" flag is set'''
        if name not in self._namespaces: raise KeyError
        else:
            if remove: self._namespaces[name].remove
            self._namespaces.pop(name, None)


class metadata_namespace(MutableMapping):
    def __init__(self, item_name, name, value=None, configuration={}, load=True, save=False):
        '''Item metadata namespace
        If "load" is set the namespace will be loaded from the registry. If it 
        exists "value" and "configuration" will be overwritten if provided. 
        If "save" is set the namespace will be written immediately to the 
        registry. This will overwrite the namespace if it exists already. 
        If the "load" flag is set the "save" flag will be ignored.'''
        log.debug("Metadata: Initializing namespace object for item '{item}' namespace '{namespace}'".format( \
            item=item_name, namespace=name))
        self._item_name = item_name
        self._name = name
        self._keyUID = MetadataKey(self._name, self._item_name)
        self._value = value
        self._configuration = configuration
        if load: 
            log.debug("Metadata: Load on initialize for item '{item}' namespace '{namespace}'".format( \
                item=item_name, namespace=name))
            self.load()
        elif save:
            log.debug("Metadata: Save on initialize for item '{item}' namespace '{namespace}' with value '{value}' and configuration'{configuration}'".format( \
                item=item_name, namespace=name, value=str(value), configuration=str(configuration)))
            self.save()
    
    def __iter__(self): return iter(self._configuration)
    def __len__(self): return len(self._configuration)
    def __setitem__(self, key, value): return self.set_config_value(key, value)
    def __getitem__(self, key): return self.get_config_value(key)
    def __delitem__(self, key): return self.delete_config_value(key)

    def load(self):
        '''Loads the namespace from the metadata registry.
        THIS WILL OVERWRITE ANY UNSAVED CHANGES TO THIS INSTANCE!'''
        log.debug("Metadata: Getting metadata for item '{item}' from namespace '{namespace}'".format( \
            item=self._item_name, namespace=self._name))
        # read from registry
        metadata = MetadataRegistry.get(self._keyUID)
        log.debug("Metadata: {metadata}".format( \
            metadata=str(metadata)))
        # parse data
        if metadata is not None: # namespace exists
            self._value = _resolveType(metadata.value)
            # load all configuration items into namespace dict
            self._configuration = {}
            for key, value in metadata.configuration.iteritems():
                self._configuration[str(key)] = _resolveType(value)

    def save(self):
        '''Saves the namespace to the metadata registry.
        (This is done automatically when changes to the value or configuration are made
        unless the "save" flag was set to false when making those changes)'''
        # convert all values to strings
        strConfiguration = {}
        for key, value in self._configuration: strConfiguration[key] = str(value)
        # save to the registry
        MetadataRegistry.add(Metadata(self._keyUID, str(self._value), strConfiguration))
        del strConfiguration

    def remove(self):
        '''Deletes this namespace from the registry.
        This instance will be preserved and can be written back to the registry.'''
        MetadataRegistry.remove(self._keyUID)

    def set_value(self, value, save=True):
        '''Sets the namespace "value".
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        self._value = value
        if save: self.save()

    @value.setter
    def value(self, value):
        '''Sets the namespace "value" and saves to the registry.'''
        return self.set_value(value)

    def get_value(self):
        '''Gets the namespace "value".'''
        return self._value

    @property
    def value(self):
        '''Returns the namespace "value".'''
        return self.get_value

    def set_config_value(self, key, value, save=True):
        '''Sets the namespace configuration value for the specified key.
        You can also use the dict method "metadata_namespace[key] = value"
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        self._configuration[str(key)] = value
        if save: self.save()

    def get_config_value(self, key):
        '''Gets the value for the specified configuration key.
        You can also use the dict method "value = metadata_namespace[key]"'''
        return self._configuration.get(str(key))

    def delete_config_value(self, key, save=True):
        '''Deletes the specified key from the configuration.
        You can also use the dict method "del metadata_namespace[key]"
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        self._configuration.pop(str(key), None)
        if save: self.save()

    def set_configuration(self, configuration, save=True):
        '''Allows setting the entire configuration dict.
        THIS WILL OVERWRITE THE EXISTING CONFIGURATION DICT!
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        if not isinstance(configuration, dict): raise TypeError
        self._configuration = configuration

    def add_configuration(self, configuration, save=True):
        '''Allows adding an iterable list or dict of new key-value pairs to the configuration.
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        self._configuration.update(configuration)
        if save: self.save()

    def clear_configuration(self, save=True):
        '''Clears all keys and values in the configuration dict.
        Set "save" flag to False to skip saving to openHAB. You must take care to manually save
        using the "save()" method or setting another element with the "save" flag set to True.'''
        self._configuration = {}
        if save: self.save()
