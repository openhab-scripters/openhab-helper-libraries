/*
This library provides functions for manipulating Item Metadata.
*/

'use strict';

(function(context) {
    'use strict';

    var log = Java.type("org.slf4j.LoggerFactory").getLogger("jsr223.javascript.core.metadata");

    var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
    load(OPENHAB_CONF + '/automation/lib/javascript/core/osgi.js');

    try {
        var MetadataRegistry = get_service("org.openhab.core.items.MetadataRegistry");
    } catch(e) {
        var MetadataRegistry =  get_service("org.eclipse.smarthome.core.items.MetadataRegistry");
    }

    try {
        var Metadata = Java.type("org.openhab.core.items.Metadata");
        var MetadataKey = Java.type("org.openhab.core.items.MetadataKey");
    } catch(e) {
        var Metadata = Java.type("org.eclipse.smarthome.core.items.Metadata");
        var MetadataKey = Java.type("org.eclipse.smarthome.core.items.MetadataKey");
    }

    context._merge_configuration = function(metadata_configuration, new_configuration) {
        var old_configuration = {};
        for (var property in metadata_configuration) {
            old_configuration[property] = metadata_configuration[property];
        }
    
        for (var property in new_configuration) {
            old_configuration[property] = new_configuration[property];
        }
        return old_configuration;
    }

    context.get_all_namespaces = function(item_name) {
        /*
        This function will return an array of an Item's namespaces.

        Args:
            item_name (string): name of the Item to retrieve namespaces names from

        Returns:
            array of strings representing the namespace names found for the
                specified Item
            false: Item does not exist

        Raises:
            TODO: ValueError: Item does not exist
        */
        try {
            var namespace_names = [];
            log.debug("Getting all namespaces: Item [{}]", item_name);
            MetadataRegistry.getAll()
                .stream()
                .filter(function(metadata) {
                    return metadata.UID.itemName == item_name;
                })
                .forEach(function(metadata) {
                    namespace_names.push(metadata.UID.namespace);
                });

            return namespace_names;
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.get_metadata = function(item_name, namespace) {
        /*
        This function will return the Metadata object associated with the
        specified Item.

        Args:
            item_name (string): name of the Item.
            namespace (string): name of the namespace.

        Returns:
            Metadata object: contains the namespace ``value`` and
                ``configuration`` dictionary
            null: namespace or metadata does not exist for the Item
            false: namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Getting metadata: Item [{}], namespace [{}]", item_name, namespace);
            var metadata = MetadataRegistry.get(new MetadataKey(namespace, item_name));
            return metadata;
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.set_metadata = function(item_name, namespace, configuration, value, overwrite) {
        /*
        This function creates or modifies Item metadata, optionally overwriting
        the existing data. If not overwriting, the provided keys and values will
        be overlaid on top of the existing keys and values.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            configuration (object): ``configuration`` object to add to the
                namespace
            value (string): either the new namespace value or ``null``
            overwrite (bool): if ``true``, existing namespace data will be
                discarded

        Returns:
            true: Operation completed
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            overwrite = overwrite || false;
            value = value || null;
            if (overwrite) {
                remove_metadata(item_name, namespace);
            }
            var metadata = get_metadata(item_name, namespace);
            if (metadata === false) {
                log.debug("Set metadata: Item or namespace does not exist: Item [{}], namespace [{}]", item_name, namespace);
                return false;
            } else {
                var result = null
                if (metadata === null || overwrite) {
                    log.debug("Adding or overwriting metadata namespace with [value: {}, configuration: {}]: Item [{}], namespace [{}]", [value, JSON.stringify(configuration), item_name, namespace]);
                    result = MetadataRegistry.add(new Metadata(new MetadataKey(namespace, item_name), value, configuration));
                } else {
                    if (!value) {
                        value = metadata.value;
                    }
                    var new_configuration = _merge_configuration(metadata.configuration, configuration);
                    log.debug("Setting metadata namespace to [value: {}, configuration: {}]: Item [{}], namespace [{}]", [value, JSON.stringify(new_configuration), item_name, namespace]);
                    result = MetadataRegistry.update(new Metadata(new MetadataKey(namespace, item_name), value, new_configuration));
                }
                return (result === null ? false : true);
            }
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.remove_metadata = function(item_name, namespace) {
        /*
        This function removes the Item metadata for the specified namepsace or for
        all namespaces.

        Args:
            item_name (string): name of the item
            namespace (string): name of the namespace or ``null``, which will
                remove metadata in all namespaces for the specified Item

        Returns:
            true: Operation completed
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            namespace = namespace || null;
            if (!namespace) {
                log.debug("Deleting all metadata: Item [{}]", item_name);
                MetadataRegistry.removeItemMetadata(item_name);
            } else {
                log.debug("Deleting metadata: Item [{}], namespace [{}]", item_name, namespace);
                MetadataRegistry.remove(new MetadataKey(namespace, item_name));
            }
            return true;
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.get_value = function(item_name, namespace) {
        /*
        This function will return the Item metadata ``value`` for the specified
        namespace.

        Args:
            item_name (string): name of the item
            namespace (string): name of the namespace

        Returns:
            value: namespace ``value``, can be ``null``
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Getting namespace value: Item [{}], namespace [{}]", item_name, namespace);
            var metadata = get_metadata(item_name, namespace);
            return metadata.value;
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.set_value = function(item_name, namespace, value) {
        /*
        This function creates or updates the Item metadata ``value`` for the
        specified namespace.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            value (string): new or updated value for the namespace

        Returns:
            true: Operation completed
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Setting namespace value: Item [{}], namespace [{}], value [{}]", [item_name, namespace, value]);
            var metadata = get_metadata(item_name, namespace);
            return set_metadata(item_name, namespace, metadata.configuration, value, true);
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.get_key_value = function(item_name, namespace, key) {
        /*
        Ths function returns the ``configuration`` value for the specified key.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            key (string): ``configuration`` key to return

        Returns:
            value: ``configuration`` key value, can be ``null``
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Getting value for key: Item [{}], namespace [{}], key [{}]", [item_name, namespace, key]);
            var metadata = get_metadata(item_name, namespace);
            return metadata.configuration[key];
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.set_key_value = function(item_name, namespace, key, value) {
        /*
        This function creates or updates a ``configuration`` value in the
        specified namespace. This function cannot be used unless the namespace
        already exists.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            key (string): ``configuration`` key to create or update
            value (string or decimal): value to set for ``configuration`` key

        Returns:
            true: Operation completed
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Setting value for key: Item [{}], namespace [{}], key [{}], value [{}]", [item_name, namespace, key, value]);
            var metadata = get_metadata(item_name, namespace);
            var new_configuration = {};
            new_configuration[key] = value;
            if (metadata) {
                new_configuration = _merge_configuration(metadata.configuration, new_configuration);
            }
            return set_metadata(item_name, namespace, new_configuration);
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

    context.remove_key_value = function(item_name, namespace, key) {
        /*
        This function removes a ``configuration`` key and its value from the
        specified namespace.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            key (string): ``configuration`` key to remove

        Returns:
            true: Operation completed
            false: Item does not exist or namespace name is invalid

        Raises:
            TODO: ValueError: Item does not exist
            IllegalArgumentException: namespace name is invalid
        */
        try {
            log.debug("Removing key: Item [{}], namespace [{}], key [{}]", [item_name, namespace, key]);
            var metadata = get_metadata(item_name, namespace);
            if (metadata) {
                var new_configuration = _merge_configuration(metadata.configuration, {});
                delete new_configuration[key];
                return set_metadata(item_name, namespace, new_configuration, metadata.value, true);
            } else {
                log.debug("Removing key: metadata does not exist: Item [{}], namespace [{}]", item_name, namespace);
                return false
            }
        } catch(e) {
            log.warn(e);
            return false;
        }
    };

})(this);