********
Settings
********

    Eos uses settings stored in metadata to determined what state a light
    should be in for a given scene. The :doc:`Editor` is the recommended way
    to modify settings. Read on for more information about settings and how Eos
    discovers them.

    .. caution::

        It is not recommended to set Eos metadata in items files as this will
        prevent the *Eos Editor* from being able to modify them.

*Fixed* Scenes
==============

    *   ``state`` will be used as a fixed value to evaluate the scene.

*Threshold* Scenes
==================

    *   ``level_source`` should be a valid item who's state will be compared to
        *level_threshold*.

    *   ``level_threshold`` is compared to *level_source*.

    *   ``state_above`` will be used as a fixed value to evaluate the scene if
        the *level_source* is above *level_threshold*.

    *   ``state_below`` will be used as a fixed value to evaluate the scene if
        the *level_source* is equal to or below *level_threshold*.

*Scaled* Scenes
===============

    *   ``level_source`` should be a valid item who's state will be compared to
        *level_high* and *level_low*.

    *   ``level_high`` and ``level_low`` define the range of values for
        *level_source* that will be used to scale the light's state.

    *   ``state_high`` and ``state_low`` define the range of state for the
        light. The command sent to the light will be scaled between
        *state_high* and *state_low* in relation to where *level_source* falls
        between *level_high* and *level_low*.

    *   ``state_above`` will be used as a fixed value to evaluate the scene if
        *level_source* is above *level_high*. If this setting is not provided,
        *state_high* will be used instead.

    *   ``state_below`` will be used as a fixed value to evaluate the scene if
        *level_source* is below *level_low*. If this setting is not provided,
        *state_low* will be used instead.


Motion Settings
===============

    Eos supports motion triggers for all scene types. You can define a state or
    provide the name of another scene to be evaluated if motion is detected. If
    motion is not detected then the scene is evaluated normally. These settings
    don't have to be used with motion sensors, any item can be provided to use
    as a trigger.

    *   ``motion_source`` should be a valid item who's state will be checked
        against *motion_active*.

    *   ``motion_active`` is the state of *motion_source* that indicates motion
        is detected. If motion is detected and *motion_state* is defined, it
        will be used as a fixed value to evaluate the scene; otherwise
        *motion_scene* will be evaluated for the light, ignoring any motion
        settings.

    *   ``motion_state`` will be used as a fixed value to evaluate the scene if
        motion is active.

    *   ``motion_scene`` should be the name of a scene to evaluate if motion is
        active. Any motion options in the specified scene will be ignored.


Search Pattern
==============

    Settings can be defined in a lazy manner, that is, you only need to define
    a setting once in the least specific location that applies. It is important
    to understand how Eos looks for settings to know the best place to put a
    setting.

    The following table shows the locations Eos looks for settings, in order of
    most to least specific (referred to as *depth*):

    =====   =================== ======================================================
    Depth   Location            Description
    =====   =================== ======================================================
    1       *item-scene*        Scene definition in Item metadata
    2       *group-type-scene*  Scene definition in Light Type data in Group metadata
    3       *group-scene*       Scene definition in Group metadata
    4       *global-type-scene* Scene definition in Light Type data in Global settings
    5       *global-scene*      Scene definition in Global settings
    6       *item*              Item metadata
    7       *group-type*        Light Type data in Group metadata
    8       *group*             Group metadata
    9       *global-type*       Light Type data in Global settings
    10      *global*            Global settings
    =====   =================== ======================================================

    .. note::

        No *state* settings are valid a depths 3, 5, 8, or 10. This is because
        *state* settings are different for each Light type and settings at
        these depths are not specific to a Light type. This includes ``state``,
        ``state_high``, ``state_low``, ``state_above``, and ``state_below``.

    When evaluting a scene, Eos will look for each of the settings it needs for
    the scene in each of the locations shown above and use the first occurance
    it finds. Settings for a scene do not need to be defined at the same depth,
    Eos will always use the setting at the shallowest depth, regardless of
    where other scene settings were found.


Options
=======

    * **Enabled**

        This appears as ``Enabled`` in the editor and is represented in openHAB
        as the metadata value. Setting the ``eos`` metadata namespace value to
        ``False`` will stop Eos from looking in groups or processing commands
        for lights. If no ``eos`` metadata namespace exists Eos will assume
        that groups are enabled and lights are disabled.

    * ``follow_parent``

        This setting only applies for groups. Setting it to ``False`` will stop
        the group scene being changed to ``"parent"`` when the group's parent's
        scene changes. You can still manually set the group's scene to
        ``"parent"`` if you want. The default is ``True`` if not specified.
