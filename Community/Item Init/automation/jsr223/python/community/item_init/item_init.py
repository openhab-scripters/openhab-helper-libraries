"""
Author: Rich Koshak

Rule that looks for init metadata and uses it to initialize an Item's state.

License
=======
Copyright (c) contributors to the openHAB Scripters project
"""
from core.rules import rule
from core.triggers import when
from core.metadata import get_value, get_key_value, remove_metadata
from core.utils import postUpdate, post_update_if_different

@rule("Initialize configured Items",
      description="Updates Items with an initialization value",
      tags=["init"])
@when("System started")
def item_init(event):
    """
    Rule that triggers at System started and populates Items with an initial
    value. The initialization value is defined in metadata with three key/values.
        - value: value to send update the Item to
        - override: whether to update to this value even if the Item already
            has a value. It's an optional key and should be either absent,
            "true", or "false"
        - clear: whether to delete the metadata once the Item is updated. It's
            an optional key and should be either absent, "true", or "false"

    For example:
        - { init=""[value="ON", override="true", clear="true"] }: Initialize
            the Switch Item to ON whether or not it already has a value and then
            delete the metadata.
        - { init=""[value="123,45,67"] }: Initialize the Color Item to the value
            only if it is NULL or UNDEF.

    Limitations:
        - The clear option only works for Items not created through .items
            files. For Items defined in .items files, you must manually remove
            the metadata or else it will get reloaded next time the file is
            loaded.
    """

    for item_name in [i for i in items if get_value(i, "init") is not None]:
        value = get_key_value(item_name, "init", "value")

        if get_key_value(item_name, "init", "override") == "true":
            post_update_if_different(item_name, value)
            item_init.log.debug("Overriding current value {} of {} to {}"
                                .format(items[item_name], item_name, value))
        elif isinstance(items[item_name], UnDefType):
            item_init.log.debug("Initializing {} to {}"
                                .format(item_name, value))
            postUpdate(item_name, value)

        # only works if Items are not defined in .items files
        if get_key_value(item_name, "init", "clear") == "true":
            item_init.log.debug("Removing init metadata from {}"
                                .format(item_name))
            remove_metadata(item_name, "init")
