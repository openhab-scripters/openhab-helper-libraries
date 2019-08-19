***************
Getting Started
***************

After following the steps on this page you will have installed and configured
Eos with a single group, scene item, and light, and have a basic understanding
of how Eos works.

#.  **Eos configuration**

        The first step is to add some entries to your ``configuration.py``:

        *   You must provide the name of the main group Eos should work from.
            All other Eos groups and lights should be placed in this group. Ex:

            .. code-block::

                eos_master_group = "eos_master_group"

        *   Eos uses a *Scene* item to receive scene commands for a group. A
            *Scene* item is an openHAB *String* item matching the prefix and
            suffix you define. To set the scene for a group, send the name of
            the scene as a command to the group's *Scene* item. Each group must
            have exactly one *Scene* item. The following will match the *Scene*
            item ``eos_master_scene``:

                .. code-block::

                    eos_scene_item_prefix = "eos_"
                    eos_scene_item_suffix = "_scene"

        *   Eos also supports reloading while openHAB is running, allowing you
            to add lights and groups without having to restart openHAB. You
            need to provide Eos with the name of a *Switch* item to use for
            this. Eos will reload if this item receives an ``ON`` command.

                .. code-block::

                    eos_reload_item_name = "eos_reload"

        You should now have the following in your ``configuration.py``:

            .. code-block::

                # Eos Lighting System
                eos_master_group = "eos_master_group"
                eos_scene_item_prefix = "eos_"
                eos_scene_item_suffix = "_scene"
                eos_reload_item_name = "eos_reload"

#.  **Create Items and Groups**

        Next we will create the *master group* we configured in the previous
        step, as well as a *Scene* item for it. We will also add a *Switch*
        item that we will use as a test light, and another to reinitialize Eos.
        These examples show how to do this using ``.items`` files, but you can
        also add them using the UI of your choosing.

        In an items file or using a UI, add the following items:

            .. code-block::

                Group eos_master_group "Eos Master Group"
                String eos_master_scene "Eos Master Scene [%s]" (eos_master_group)
                Switch eos_test_light "Test Light" (eos_master_group)

                Switch eos_reload "Reload Eos" { autoupdate="false" }

        Now we will add these items to a sitemap so we can see them:

            .. code-block:: Java

                sitemap eos label="eos" {
                    Selection item=eos_master_scene mappings=["on"="On", "off"="Off"]
                    Switch item=eos_test_light

                    Switch item=eos_reload mappings=[ON="Reload"]
                }

        The ``"on"`` and ``"off"`` scenes shown in the above example are
        default scenes that come with Eos to help you get started.

#.  **Install Eos - Part 1**

    |   Copy or link the
        ``Community/Eos Lighting/automation/lib/python/community/eos``
        directory into ``{OH_CONF}/automation/lib/python/community``.

#.  **Enable Test Light**

        Now we need to enable the test light we created so that Eos will see
        it. Eos includes an editor that makes configuring scene settings in
        metadata simple, without needing to edit the metadata by hand.

            In order to run the Eos Editor you will need to have Python 3.x
            installed and a few dependencies. Install the dependencies with the
            following command:

                .. code-block:: none

                    pip3 install prompt_toolkit==2.0.7 click pygments requests

            To launch the Eos Editor run:

                .. code-block:: none

                    python3 {OH_CONF}/automation/lib/python/community/eos/editor

            You should now see the following group navigation menu:

                .. image:: images/getstart1.png

            As you can see, when you first add a light to openHAB it will
            appear in the editor as a *Non Eos Item* and will not be controlled
            by Eos. To enable a light to be controlled by Eos, simply select
            the item in the editor and select *Save*.

                .. image:: images/editor-light.png

            The item will now appear in the *Eos Lights* category.

                .. image:: images/getstart3.png

#.  **Install Eos - Part 2**

    |   Copy or link the
        ``Community/Eos Lighting/automation/jsr223/python/community/eos``
        directory into ``{OH_CONF}/automation/jsr223/python/community``.
    |   Eos will be loaded immediately and you should see the following log
        entries:

        .. code-block:: none

            [INFO ] [jsr223.jython.community.eos          ] - Eos initializing...
            [INFO ] [jsr223.jython.community.eos          ] - Eos initialized

#.  **Control the Light**

    You should now be able to control the test light using the scene item!

        .. image:: images/getstart4.png

#.  **Next Steps**

    You should now read the rest of the documentation to familiarize yourself
    with all of the concepts in Eos.
