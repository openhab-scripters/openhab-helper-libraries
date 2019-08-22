*************
Configuration
*************


Eos requires a few values to be provided in the ``configuration.py`` file for
it to work. See below for a detailed reference of all options.

An example file (``configuration.py.example``) is provided with Eos, it's
contents are also shown here:

.. code-block::

    # Eos Lighting System
    eos_master_group = "eos_master_group"
    eos_scene_item_prefix = "eos_"
    eos_scene_item_suffix = "_scene"
    eos_reload_item_name = "eos_reload"
    eos_global_settings = {}


*   ``eos_master_group`` is the name of the master group that all Eos groups
    and lights must go within. Groups can be nested as deeply as you need for
    your setup.

*   ``eos_scene_item_prefix`` and ``eos_scene_item_suffix`` provide Eos with a
    pattern to use to identify which *String* item in a group is the scene
    item. You may provide one or both of these settings.

*   ``eos_reload_item_name`` is the name of a *Switch* item to allow on-the-fly
    reinitialization of Eos. Sending the command ``ON`` to this switch will
    reinitialize Eos, causing it to scan all groups and lights again and
    detecting any new light or groups you may have added.

*   ``eos_global_settings`` allows you to provide a ``dict`` of Eos settings
    that are visible to all items. Eos comes with a few Global settings already
    defined to get you started, if you want to remove any of them just set the
    value to ``None`` here. Any settings you put here will be added to the
    built-in Global settings shown below and will overwrite any existing
    values.

    Because groups inherit settings from their parent group, you can also put
    settings in the *master group* with the same effects. This allows you to
    use the *Eos Editor* to define the scenes and settings you want to be
    global, instead of writing them out here.

  .. code-block::

    {
        "switch": {     # 'switch' type lights
            "on": {         # 'on' scene
                # this is depth 4
                "state": "ON"
            },
            "off": {        # 'off' scene
                "state": "OFF"
            },
            # this is depth 9
            "state": "OFF",
            "state_above": "OFF",
            "state_below": "ON"
        },

        "dimmer": {     # 'dimmer' type lights
            "on": {         # 'on' scene
                "state": 100
            },
            "off": {        # 'off' scene
                "state": 0
            },
            "state": 0,
            "state_high": 0,
            "state_low": 100
        },

        "color": {      # 'color' type lights
            "on": {         # 'on' scene
                "state": 100
            },
            "off": {        # 'off' scene
                "state": 0
            },
            "state": 0,
            "state_high": 0,
            "state_low": 100
        },

        # this is depth 10
        "motion_active": "ON",
        "motion_scene": "on"
    }
