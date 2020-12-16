/**
 * Functions for creating rules
 * 
 * Copyright (c) 2019 Contributors to the openHAB Scripters project
 * 
 * @author Jonathan Gilbert - initial contribution
 */

var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
load(OPENHAB_CONF+'/automation/lib/javascript/core/osgi.js');


(function(context) {
    'use strict';	

var itemBuilderFactory = get_service(
        "org.openhab.core.items.ItemBuilderFactory"
    ) || get_service(
        "org.eclipse.smarthome.core.items.ItemBuilderFactory"
    )

var managedItemProvider = get_service(
        "org.openhab.core.items.ManagedItemProvider"
    ) || get_service(
        "org.eclipse.smarthome.core.items.ManagedItemProvider"
    )

var HashSet = Java.type("java.util.HashSet");;


    /*
        itemName (str): Item name for the Item to create
        itemType (str): (optional) the type of the Item
        category (str): (optional) the category (icon) for the Item
        groups (str): (optional) a list of groups the Item is a member of
        label (str): (optional) the label for the Item
        tags (list): (optional) a list of tags for the Item
        giBaseType (str): (optional) the group Item base type for the Item
        groupFunction (GroupFunction): (optional) the group function used by the Item
            
        returns: the item object, or undefined otherwise  
    */
context.addItem = function(itemName, itemType, category, groups, label, tags, giBaseType, groupFunction) {
    var baseItem;
    if(itemType !== 'Group' && typeof(giBaseType) !== 'undefined') {
        baseItem = itemBuilderFactory.newItemBuilder(giBaseType, itemName + "_baseItem").build()
    }
    if(itemType !== 'Group') {
        groupFunction = undefined;
    }

    var builder = itemBuilderFactory.newItemBuilder(itemType, itemName).
                                                withCategory(category).
                                                withLabel(label).
                                                withGroups(groups);

    builder = builder.withTags(new HashSet(tags));

    if(typeof baseItem !== 'undefined') {
        builder = builder.withBaseItem(baseItem);
    }
    if(typeof groupFunction !== 'undefined') {
        builder = builder.withGroupFunction(groupFunction);
    }

    var item = builder.build();
    managedItemProvider.add(item);
    logDebug("Item added: " + item);
    return item;
}

context.removeItem = function(itemOrItemName) {
    var itemName;

    if(typeof itemOrItemName === 'string') {
        itemName = itemOrItemName;
    } else if(itemOrItemName.hasOwnProperty('name')) {
        itemName = itemOrItemName.name;
    } else {
        logWarn('Item not registered so cannot be removed');
        return null;
    }

    if(getItem(itemName) === null) {
        logWarn('Item not registered so cannot be removed');
        return null;
    }

    managedItemProvider.remove(itemName);

    if(getItem(itemName) === null) {
        logDebug("Item removed: " + itemName);
        return itemName;
    } else {
        logWarn("Failed to remove item: " + itemName);
        return null;
    }
}

})(this);
