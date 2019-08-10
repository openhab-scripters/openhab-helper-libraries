********
Triggers
********


    The following is a list of available triggers for use with the ``when`` Decorator.
    Any text in ``CAPITAL LETTERS`` should be replaced with a value specific to your use case, and anything in square brackets (``[]``) is optional.

    If you are looking for more information on these triggers as :ref:`Guides/Rules:Extensions`,
    it can be found in the Core Triggers documentation for the language of your choice.


Items and Groups
================

    Item and Group event triggers catch commands and state changes or updates.

    * The ``Item`` trigger can be used to catch events from an item or group.
    * The ``Member of`` trigger will catch events from any member (item or group) of the specified group, but not the group itself.
    * ``Descendent of`` creates a trigger for every item in the specified group, and every item in any groups within recursively.
      It will not create triggers for any groups, however.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @when("Item ITEM_NAME received update [NEW_STATE]")
                @when("Item GROUP_NAME received update [NEW_STATE]")
                @when("Member of GROUP_NAME received update [NEW_STATE]")
                @when("Descendent of GROUP_NAME received update [NEW_STATE]")

                @when("Item ITEM_NAME changed [from OLD_STATE] [to NEW_STATE]")
                @when("Item GROUP_NAME changed [from OLD_STATE] [to NEW_STATE]")
                @when("Member of GROUP_NAME changed [from OLD_STATE] [to NEW_STATE]")
                @when("Descendent of GROUP_NAME changed [from OLD_STATE] [to NEW_STATE]")

                @when("Item ITEM_NAME received command [COMMAND]")
                @when("Item GROUP_NAME received command [COMMAND]")
                @when("Member of GROUP_NAME received command [COMMAND]")
                @when("Descendent of GROUP_NAME received command [COMMAND]")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                Item ITEM_NAME received update [NEW_STATE]
                Member of GROUP_NAME received update [NEW_STATE]

                Item ITEM_NAME changed [from OLD_STATE] [to NEW_STATE]
                Item GROUP_NAME changed [from OLD_STATE] [to NEW_STATE]
                Member of GROUP_NAME changed [from OLD_STATE] [to NEW_STATE]

                Item ITEM_NAME received command [COMMAND]
                Item GROUP_NAME received command [COMMAND]
                Member of GROUP_NAME received command [COMMAND]

    When using ``Member of`` or ``Descendent of`` triggers, you can get the name of the Item that triggered the event using ``event.itemName``

    .. note::

        When using the ``received command`` trigger, the rule will be triggered **BEFORE** the Item's state gets updated.
        You can use ``event.itemCommand`` to access the command that was sent.

    .. warning::

        If the state or command used in the ``when`` decorator has special characters, including spaces, it must be surrounded in single quotes ``'like this'`` to prevent errors.


Thing Event
===========

    Thing status changes can also be used to trigger rules.
    A list of all available statuses can be found `here <https://www.openhab.org/docs/concepts/things.html>`_.
    If you need to trigger on a specific status, you can get the status name via ``event.statusInfo.status`` and check if it is the status that you needed.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @when("Thing THING:NAME received update [NEW_STATE]")
                @when("Thing THING:NAME changed [from OLD_STATE] [to NEW_STATE]")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                Thing "THING:NAME" received update [NEW_STATE]
                Thing "THING:NAME" changed [from OLD_STATE] [to NEW_STATE]

    .. warning::

        If the status used in the ``when`` decorator has special characters, including spaces, it must be surrounded in single quotes ``'like this'`` to prevent errors.


Channel Event
=============

    Channel triggers allow you to catch events from bindings using Channels.
    You can find Channel names and events in the documentation for the binding.

    .. note::

        Only *trigger* Channels can be used with this trigger, `same as in the rules DSL <https://www.openhab.org/docs/configuration/rules-dsl.html#channel-based-triggers>`_.
        If not using a trigger Channel, you will receive a validation error when saving the script.
        The binding documentation will identify which Channels, if any, are trigger Channels.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @when("Channel CHANNEL:NAME triggered [EVENT]")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                Channel "CHANNEL:NAME" triggered [EVENT]

    If you need the name of the Channel or event that triggered the rule, they are available as ``event.channel`` and ``event.event``, respectively.

    .. warning::

        If the event used in the ``when`` decorator has special characters, including spaces, it must be surrounded in single quotes ``'like this'`` to prevent errors.


Cron
====

    Cron triggers can be used to trigger rules at specific times.
    There are a few built-in expressions; their use is shown in the examples.
    Several tools are available to help with composing cron expressions such as `CronMaker`_ or `FreeFormatter`_.
    More information can be found in the `openHAB documentation`_.

    .. _CronMaker: http://www.cronmaker.com/
    .. _FreeFormatter: http://www.freeformatter.com/cron-expression-generator-quartz.html
    .. _openHAB documentation: https://www.openhab.org/docs/configuration/rules-dsl.html#time-based-triggers

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @when("Time cron 55 55 5 * * ?")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                Time cron "55 55 5 * * ?"


System Started
==============

    The system started trigger can be used to run a rule when openHAB is first started or when the file gets reloaded.

    .. warning::

        This trigger requires snapshot build S1566 or newer, see below for a workaround for previous versions.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @when("System started")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                System started

    For builds prior to snapshot S1566, which cannot use the StartupTrigger, you can run rules on openHAB start and file reload by calling the rule function directly.
    You should create a function at the end of file called ``scriptLoaded`` and put the calls to your rules in that function.
    Here is an example of how to do that:

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Item my_item changed to ON")
                def my_rule_function(event):
                    # your Python code here

                def scriptLoaded(id):
                    # call rule function when this file is loaded
                    my_rule_function(None)

        .. group-tab:: JavaScript

            TODO

        .. group-tab:: Groovy

            TODO


System Shuts Down
=================

    There is currently no working ``"System shuts down"`` trigger.
    If attempting to use this trigger with the ``when`` decorator, you will receive a validation error when saving the script.
    Below are workarounds for executing a function when a script is unloaded, similar to what is described for ``System started``.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Item my_item changed to ON")
                def my_rule_function(event):
                    # your Python code here

                def scriptUnloaded():
                    # call rule function when this file is unloaded, but be sure an event of None is handled
                    my_rule_function(None)

        .. group-tab:: JavaScript

            TODO

        .. group-tab:: Groovy

            TODO

        .. group-tab:: Rules DSL

            .. code-block:: java

                System shuts down
