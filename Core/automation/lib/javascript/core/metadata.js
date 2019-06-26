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
        */
        var namespace_names = [];
        log.debug("get_all_namespaces: Item [{}]", item_name);
        MetadataRegistry.getAll()
            .stream()
            .filter(function(metadata) {
                return metadata.UID.itemName == item_name;
            })
            .forEach(function(metadata) {
                namespace_names.push(metadata.UID.namespace);
            });

        return namespace_names;
    };

    context.get_metadata = function(item_name, namespace) {
        /*
        This function will return the Metadata object associated with the
        specified Item.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace

        Returns:
            Metadata object: contains the namespace ``value`` and
                ``configuration`` dictionary
            null: metadata or Item does not exist
        */
        log.debug("get_metadata: Item [{}], namespace [{}]", item_name, namespace);
        return MetadataRegistry.get(new MetadataKey(namespace, item_name));
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
        */
        overwrite = overwrite || false;
        value = value || null;
        if (overwrite) {
            remove_metadata(item_name, namespace);
        }
        var metadata = get_metadata(item_name, namespace);
        if (metadata === null || overwrite) {
            log.debug("set_metadata: adding or overwriting metadata namespace with [value: {}, configuration: {}]: Item [{}], namespace [{}]", [value, JSON.stringify(configuration), item_name, namespace]);
            MetadataRegistry.add(new Metadata(new MetadataKey(namespace, item_name), value, configuration));
        } else {
            if (!value) {
                value = metadata.value;
            }
            var new_configuration = _merge_configuration(metadata.configuration, configuration);
            log.debug("set_metadata: setting metadata namespace to [value: {}, configuration: {}]: Item [{}], namespace [{}]", [value, JSON.stringify(new_configuration), item_name, namespace]);
            MetadataRegistry.update(new Metadata(new MetadataKey(namespace, item_name), value, new_configuration));
        }
    };

    context.remove_metadata = function(item_name, namespace) {
        /*
        This function removes the Item metadata for the specified namespace or
        all namespaces.

        Args:
            item_name (string): name of the item
            namespace (string): name of the namespace or ``null``, which will
                remove metadata in all namespaces for the specified Item
        */
        namespace = namespace || null;
        if (!namespace) {
            log.debug("remove_metadata (all): Item [{}]", item_name);
            MetadataRegistry.removeItemMetadata(item_name);
        } else {
            log.debug("remove_metadata: Item [{}], namespace [{}]", item_name, namespace);
            MetadataRegistry.remove(new MetadataKey(namespace, item_name));
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
            null: metadata or Item does not exist
        */
        log.debug("get_value: Item [{}], namespace [{}]", item_name, namespace);
        var metadata = get_metadata(item_name, namespace);
        if (metadata) {
            return metadata.value;
        } else {
            return null;
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
        */
        log.debug("set_value: Item [{}], namespace [{}], value [{}]", [item_name, namespace, value]);
        var metadata = get_metadata(item_name, namespace);
        if (metadata) {
            set_metadata(item_name, namespace, metadata.configuration, value, true);
        } else {
            set_metadata(item_name, namespace, {}, value);
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
            null: metadata or Item does not exist
        */
        log.debug("get_key_value: Item [{}], namespace [{}], key [{}]", [item_name, namespace, key]);
        var metadata = get_metadata(item_name, namespace);
        if (metadata) {
            return metadata.configuration[key];
        } else {
            return null;
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
            value (string, decimal, boolean): value to set for ``configuration``
                key
        */
        log.debug("set_key_value: Item [{}], namespace [{}], key [{}], value [{}]", [item_name, namespace, key, value]);
        var metadata = get_metadata(item_name, namespace);
        var new_configuration = {};
        new_configuration[key] = value;
        if (metadata) {
            new_configuration = _merge_configuration(metadata.configuration, new_configuration);
        }
        set_metadata(item_name, namespace, new_configuration);
    };

    context.remove_key_value = function(item_name, namespace, key) {
        /*
        This function removes a ``configuration`` key and its value from the
        specified namespace.

        Args:
            item_name (string): name of the Item
            namespace (string): name of the namespace
            key (string): ``configuration`` key to remove
        */
        log.debug("remove_key_value: Item [{}], namespace [{}], key [{}]", [item_name, namespace, key]);
        var metadata = get_metadata(item_name, namespace);
        if (metadata) {
            var new_configuration = _merge_configuration(metadata.configuration, {});
            delete new_configuration[key];
            set_metadata(item_name, namespace, new_configuration, metadata.value, true);
        } else {
            log.debug("remove_key_value: metadata does not exist: Item [{}], namespace [{}]", item_name, namespace);
        }
    };

})(this);
