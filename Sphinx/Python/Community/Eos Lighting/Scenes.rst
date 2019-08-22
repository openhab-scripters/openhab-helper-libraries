******
Scenes
******

    Eos controls your lights based on scenes that you define. A scene is
    referenced by name and you select it by sending the name as a command to
    the group's scene item. You can use *Selection* widgets in the sitemap, or
    another part of your home automation to send the scene commands.

    When a group's scene item receives a command, a scene update will be
    processed for the group, and any enabled groups will have their scene item
    set to the ``"parent"`` scene unless they have
    :ref:`follow_parent <Python/Community/Eos Lighting/Settings:Options>`
    disabled.

    If a group's scene item's state changes, a scene update will be processed
    for the group, but the new scene will not be propagated to child groups.
    This can be used, for example, to set the master scene based on Time of Day
    without changing any group scenes that have been set to something other
    than ``"parent"``.

    A scene update involves evaluating the scene for every enabled light in
    the group and triggering a scene update for any enabled groups that have
    their scene set to ``"parent"``.

Built-in Scenes
===============

    Eos comes with two scenes configured already, ``"on"`` and ``"off"``. They
    are very simple scenes that will just turn a light on, or off, as their
    names suggest. You may override these scenes simply by defining your own
    settings for them.

    There are also two special scenes in Eos called ``"manual"`` and
    ``"parent"``. These scenes have special behavoirs and cannot be changed.
    The ``"manual"`` scene does as it's name suggests and allows manual control
    of the lights in the group, Eos will not send any commands to the lights.
    The ``"parent"`` scene will cause the group to use the scene from it's
    parent group. This can be used to control an entire floor or your whole
    home from a single scene item, for example.

Types
=====

    There are 3 types of scene in Eos, determined based on what settings are
    found first. Each one uses different settings and determines the light
    state in different ways.

*Fixed*
-------

        *Fixed* type scenes are the simplest, the setting ``state`` is used as
        a fixed value for state when evaluating the scene.

        A *Fixed* type scene is selected if Eos finds a ``state`` setting.

        Any light type can be used with *Fixed* type scenes.

*Threshold*
-----------

        *Threshold* type scenes add a bit of automation to light control. They
        require a ``state_above`` and ``state_below`` setting. You also need to
        specify a ``level_source`` item who's state will be used as the
        *Level*, most commonly this will be a lux level but you are not limited
        to this. Lastly you need a ``level_threshold``, if the level is above
        the threshold, ``state_above`` will be used as a fixed value when
        evaluating the scene, otherwise ``state_below`` will be used.

        A *Threshold* type scene is selected if Eos finds a ``level_threshold``
        setting.

        Any light type can be used with *Threshold* type scenes.

        .. note::

            Eos creates a rule when it initializes that triggers on changes to
            ``level_source`` item states. If you change the ``level_source``
            setting without reinitializing Eos the scene will still be
            evalutated correctly, but Eos will not know when the item's state
            changes and will not update the light automatically.

*Scaled*
--------

        *Scaled* type scenes are the most powerful and offer dynamic control of
        your lights. As the name suggests, *Scaled* scenes allow Eos to dim a
        light based on a *Level*, most commonly a lux level but you are not
        limited to that. A ``level_source`` item provides the *Level* used for
        the scene. The ``level_high`` and ``level_low`` settings define a range
        of levels to scale between, and ``state_high`` and ``state_low`` set
        the range of states to scale between when the level is between
        ``level_high`` and ``level_low``. If the level is outside that range,
        ``state_above`` and ``state_below`` will be used as fixed values for
        evaluating the scene if they are present, otherwise ``state_high`` and
        ``state_low`` will be used in their place.

        A *Scaled* type scene is selected if Eos finds a ``level_high`` or
        ``level_low`` setting, or if it finds a ``state_high`` or ``state_low``
        setting in a scene definition (depths 1-5).

        Only *Dimmer* and *Color* type lights can be used with *Scaled* scenes.

        .. note::

            Eos creates a rule when it initializes that triggers on changes to
            ``level_source`` item states. If you change the ``level_source``
            setting without reinitializing Eos the scene will still be
            evalutated correctly, but Eos will not know when the item's state
            changes and will not update the light automatically.

Inferring Type
==============

    The scene type is inferred based on the settings Eos finds. Settings used
    to infer scene types are listed above for each scene type.

    #.  Eos will first look for a *Fixed* type scene at depths 1-5
        (see :ref:`Python/Community/Eos Lighting/Settings:Search Pattern` for
        a description of depths), if it finds a telltale setting it will assume
        the scene is a *Fixed* type.
    #.  If it did not find a *Fixed* type scene, and the light is a *Dimmer*
        or *Color* type, it will look for a *Scaled* type scene.
    #.  If it did not find a *Scaled* type scene or if the light is a *Switch*
        type, it will look for a *Threshold* type scene.
    #.  If a scene type has not yet been determined, Eos will repeat the above
        search at depths 6-10.
