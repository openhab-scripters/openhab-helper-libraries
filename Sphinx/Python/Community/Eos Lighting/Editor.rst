**********
Eos Editor
**********

Included with Eos is an Editor to simplify creating and modifying scenes and
settings.

Launching
=========

    In order to run the *Eos Editor* you will need to install Python 3.x and
    some dependencies. If you followed the :doc:`Getting Started` instructions
    you should already have these installed. If you do not, the following
    command will install the dependencies for the *Eos Editor*:

    .. code-block:: none

        pip3 install prompt_toolkit==2.0.7 click pygments requests

    Use the following command to launch the *Eos Editor*:

    .. code-block:: none

        python3 {OH_CONF}/automation/lib/python/community/eos/editor

    For detailed information on commands and options for the editor, run:

    .. code-block:: none

        python3 {OH_CONF}/automation/lib/python/community/eos/editor --help


Navigation Menu
===============

    The *Navigation* menu allows you to navigate all lights, groups, and non Eos
    items in a group.

    .. image:: images/editor-nav.png

    *   Displayed at the top is the current group (``eos_example_group`` in
        this case) and its parent group if it has one.
    *   *Eos Lights* in the group are shown, selecting one will open the *Edit
        Light* menu for that light.
    *   Any *Eos Groups* that are a member of the current group are shown,
        selecting one will open the *Navigation* menu for that group.
    *   *Non Eos Items* shows a list of items in the group that could be Eos
        lights or groups, selecting one opens a menu to enable the item for use
        in Eos.
    *   *Configure Group* will open the *Edit Group* menu for this group.
    *   The *Add* options allow you to add existing or new items or groups to
        this group.


Edit Light Menu
===============

    The *Edit Light* menu allows you to configure scenes and settings for a
    light.

    .. image:: images/editor-light.png

    *   Displayed at the top is the current item (``eos_test_light`` in this
        case), the group it is in, and the Eos *Light* type.
    *   *Enabled* sets whether Eos will control this light (see
        :ref:`Python/Community/Eos Lighting/Settings:Options`).
    *   *Scenes* displays a list of all scenes found for this light at any
        depth along with the scene type. The shallowest location that the scene
        definition was found is displayed to the right. Selecting a scene or
        *Add* will bring you to the *Edit Scene* menu to edit the scene at
        depth 1.
    *   *Test Scene* allows you to enter the name of a scene and see what
        settings Eos will use to evaluate it, it will open the *Edit Scene*
        menu in view-only mode.
    *   *Settings* shows a list of all settings found for this light at depths
        6-10. Selecting a setting or *Add* allows you to add a value for the
        setting in this light (depth 6).
    *   *Save* will write all changes to the light, scenes, and settings to
        openHAB.
    *   *Cancel* will discard all changes made to the light.


Edit Scene Menu
===============

    The *Edit Scene* menu allows you to modify a scene definition.

    .. image:: images/editor-scene.png

    *   Displayed at the top are:

        *   the current item (``eos_test_light`` in this case)
        *   the group it is in
        *   the Eos *Light* type, unless you are editing a scene at depth 3
    *   *Scene Name* allows you to edit the name of this scene definition
    *   *Scene Type* shows you what scene type Eos has inferred based on this
        scene definition. This will always be *"unknown"* except when this menu
        is opened from a light.
    *   *Settings* shows all settings found for this scene. Based on the light
        and scene type, settings that will be used have their values
        highlighted in green, and any missing settings will be displayed with
        ``REQUIRED`` as the value. Selecting a setting or *Add* allows you to
        specify a value for the setting in this scene.
    *   *Apply* will update the scene but will not save it to openHAB, you must
        *Save* the item you are editing to save your changes to openHAB.
    *   *Cancel* will discard all changes made to the scene.


Edit Group Menu
===============

    The *Edit Group* menu allows you to edit scenes and settings for an Eos
    group.

    .. image:: images/editor-group.png

    *   Displayed at the top is the current group (``eos_master_group`` in this
        case) and its parent group if it has one.
    *   *Enabled* sets whether Eos will scan this group (see
        :ref:`Python/Community/Eos Lighting/Settings:Options`).
    *   *Follow Parent* sets whether this group will follow its parent's scene
        when it changes (see
        :ref:`Python/Community/Eos Lighting/Settings:Options`).
    *   *Light Types* lists all of the light types available in Eos, selecting
        one opens the *Edit Light Type* menu for that light type.
    *   *Scenes* displays a list of all scenes found for this group at depths
        3 and 5. The shallowest location that the scene definition was found is
        displayed to the right. Selecting a scene or *Add* will bring you to
        the *Edit Scene* menu to edit the scene at depth 3.
    *   *Settings* shows a list of all settings found for this group at depths
        8-10. Selecting a setting or *Add* allows you to add a value for the
        setting in this group (depth 8).
    *   *Save* will write all changes to the group, scenes, and settings to
        openHAB.
    *   *Cancel* will discard all changes made to the group.

Edit Light Type Menu
====================

    The *Edit Light Type* menu allows you to edit scenes and settings for
    a specific light type in a group.

    .. image:: images/editor-type.png

    *   Displayed at the top is the current group (``eos_example_group`` in
        this case), the group it is in, and the Eos *Light* type selected.
    *   *Scenes* displays a list of all scenes found for this light type at
        depths 2-5. The shallowest location that the scene definition was found
        is displayed to the right. Selecting a scene or *Add* will bring you to
        the *Edit Scene* menu to edit the scene at depth 2.
    *   *Settings* shows a list of all settings found for this light type at
        depths 7-10. Selecting a setting or *Add* allows you to add a value for
        the setting in this light type (depth 7).
    *   *Apply* will update the light type but will not save it to openHAB, you
        must *Save* the group you are editing to save your changes to openHAB.
    *   *Cancel* will discard all changes made to the light type.
