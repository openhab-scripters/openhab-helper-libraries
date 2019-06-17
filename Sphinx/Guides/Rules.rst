*****
Rules
*****

One of the primary use cases for JSR223 scripting in openHAB is to define rules for the `Next-Generation Rule Engine`_ using the `Automation API`_.
The rule engine structures rules with *Modules* (Triggers, Conditions, Actions).
Modules are further broken down into *ModuleTypes* with corresponding *ModuleHandlers*.
Scripted rules can use ModuleTypes that are already present in openHAB, and also define new ones that can be used outside of the scripting language that defined it, including rules created in the UI.

.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _Automation API: http://www.eclipse.org/smarthome/documentation/features/rules.html#java-api

When a script is loaded, it is provided with a *JSR223 scope* that `predefines a number of variables <https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required>`_.
These include the most commonly used core types and values from openHAB (e.g., State, Command, OnOffType, etc.).
This means you don't need an import statement to load them.

For defining rules, additional symbols must be defined.
Rather than using an import, these additional symbols (`presets <https://www.openhab.org/docs/configuration/jsr223.html#predefined-script-variables-all-jsr223-languages>`_) are imported using:

.. code-block::

    scriptExtension.importPreset("RuleSimple")
    scriptExtension.importPreset("RuleSupport")
    scriptExtension.importPreset("RuleFactories")

The ``scriptExtension`` instance is provided as one of the default scope variables.
The ``RuleSimple`` preset defines the ``SimpleRule`` base class.  
This base class implements a rule with a single custom Action associated with the ``execute`` function.
The list of rule triggers are provided by the triggers attribute of the rule instance.
The triggers in these examples is an instance of the ``Trigger`` class.
The constructor arguments define the trigger, the trigger type string, and a configuration.
The ``events`` variable is part of the default scope and supports access to the event bus (posting updates and sending commands).
Finally, to register the rule with the rule engine, it must be added to the ``ruleRegistry``.
This will cause the triggers to be activated and the rule will fire.

In increasing order of complexity, rules can be written using the :ref:`Guides/Rules:Decorators`, :ref:`Guides/Rules:Extensions`, or the :ref:`Guides/Rules:Raw API`.
The details for all of these methods are included here for reference, but the section on :ref:`Guides/Rules:Decorators` should be all that is needed for creating your rules.
The decorators are abstractions (simplifications) of the extensions, which are abstractions of the raw API.

.. warning::

    Take care in your choice of object names used in your rules, so as not to use one that is already included in the `default scope <https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required>`_.


Decorators
==========

The easiest way to write rules, and the most familiar if you have used the openHAB rules DSL, is using the decorators provided by this library.
`Decorators <https://wiki.python.org/moin/PythonDecorators>_` are part of the Python language and allow you to modify, or "decorate", a function, method or class.
The libraries provide a decorator called ``rule`` for defining rules and another called ``when`` for adding triggers to rules.
This section will show you how to define rules and triggers, and it will also compare their usage with the syntax of the rules DSL to help with migration.


Imports
-------

    When writing rules with the decorators, you must import the decorator functions.
    This only needs to be done once at the top of each script you will be using them in.
    Two simple lines at the top of your file will accomplish this:

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.rules import rule
                from core.triggers import when

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            The rules DSL does not require imports for creating rules or triggers.


@rule
-----

    The first step to creating a decorated rule is to give it a name that is unique in your openHAB configuration, and optionally a description and tags:
    The optional ``description`` allows for more detail about what a rule does and is displayed in the UI.
    The ``tags`` list is also optional, and useful for categorizing rules to simplifying searches.
    The decorator adds a log attribute based on the name of the decorated class or function, but ``self.log`` can be overridden in a constructor (see :ref::`Extensions`).
    A UID attribute is also added, which makes it easier to get the rule object once it has been created.
    This can be used to enable/disable the rule.
    Finally, the decorator wraps the function or classes' ``execute`` function in a wrapper that will print nicer stack trace information, if an exception is thrown.

    .. tabs::

        .. group-tab:: Python

            .. code-block:: python

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                rule "Rule Name"


@when
-----

    Next, we'll add triggers to the rule using the ``when`` decorator.
    You may add as many or as few triggers as you want.
    The syntax for ``when`` is quite simple, and has been made with functionality similar to the rules DSL:

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Time cron 0/10 * * * * ?")
                @when("Item Test_Switch_1 received update")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                rule "Rule Name"
                when
                    Item my_item changed to ON

    The full list of triggers and details on each one can be found on the
    :doc:`../Guides/Triggers` page.


Function
--------

    Finally the last piece is the actual code of your rule, which is a function.
    The name of this function must be unique within the file it is in.
    It must be able to accept one positional argument, which will always be ``event`` in this documentation.

    The rule decorator adds some helpful attributes to the function.
    The rule UID is useful when enabling/disabling rules, ``my_rule_function.UID``.
    A logger is also provided for each rule, ``my_rule_function.log.info("Log message")``, and it will use the logger ``<core.logging.LOG_PREFIX>.Rule_Name``.
    More information on logging can be found on the :doc:`../Guides/Logging` page.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Time cron 0/10 * * * * ?")
                @when("Item Test_Switch_1 received update")
                def my_rule_function(event):
                    my_rule_function.log.info("Hello World!")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                rule "Rule Name"
                when
                    Item my_item changed to ON
                then
                    // your DSL code here
                end


Extensions
==========

    The following example shows how the rule decorator is used to decorate a class.
    The ``rule`` decorator adds the SimpleRule base class and will call ``getEventTriggers`` to get the triggers, or you can define a constructor and set ``self.triggers`` to your list of triggers (commented out in the example).
    As we get closer to the raw API, you can appeciate the amount of complexity that is removed by using the decorators.

    .. note::

        Trigger names must be unique within the scope of a rule instance, and can only contain alphanumeric characters, hythens, and underscores (no spaces)... ``[A-Za-z0-9_-]``.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.rules import rule
                from core.triggers import StartupTrigger, CronTrigger, ItemStateUpdateTrigger

                @rule("Jython Hello World (CronTrigger extension with rule decorator)", description="This is an example rule using a CronTrigger extension and rule decorator", tags=["Example rule tag"])
                class ExampleExtensionRule(object):
                    #def __init__(self):
                    #    self.triggers = [StartupTrigger().trigger,
                    #                     CronTrigger("0/10 * * * * ?").trigger,
                    #                     ItemStateUpdateTrigger("Test_Switch_1").trigger]
                    
                    def getEventTriggers(self):
                        return [StartupTrigger().trigger,
                                CronTrigger("0/10 * * * * ?").trigger,
                                ItemStateUpdateTrigger("Test_Switch_1").trigger]

                    def execute(self, module, inputs):
                        self.log.info("Hello World!")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators and Extensions have not yet been created for the Groovy helper libraries.

    The following example shows how to create a rule using an extension without the rule decorator.
    Note the use of the scriptExtensions, which were not needed with the decorators.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.triggers import StartupTrigger, CronTrigger, ItemStateUpdateTrigger
                from core.log import logging, LOG_PREFIX

                scriptExtension.importPreset("RuleSupport")
                scriptExtension.importPreset("RuleSimple")

                class CronTriggerExtension(SimpleRule):
                    def __init__(self):
                        self.triggers = [StartupTrigger().trigger,
                                         CronTrigger("0/10 * * * * ?").trigger,
                                         ItemStateUpdateTrigger("Test_Switch_1").trigger]
                        self.name = "Jython Hello World (CronTrigger extension)"
                        self.description = "This is an example Jython rule using a CronTrigger extension"
                        self.tags = set("Example rule tag")
                        self.log = logging.getLogger("{}.Hello World (CronTrigger extension)".format(LOG_PREFIX))

                    def execute(self, module, inputs):
                        self.log.info("Hello World!")

                automationManager.addRule(CronTriggerExtension())

        .. group-tab:: JavaScript

            .. code-block::

                'use strict';

                var OPENHAB_CONF = Java.type("java.lang.System").getenv("OPENHAB_CONF");
                load(OPENHAB_CONF+'/automation/lib/javascript/core/rules.js');
                var me = "HelloWorld.js";

                JSRule({
                    name: "Javascript Hello World (GenericCronTrigger raw API with JS helper libraries)",
                    description: "This is an example Jython cron rule using the raw API",
                    triggers: [
                        TimerTrigger("0/10 * * * * ?")
                    ],
                    execute: function( module, inputs){
                        logInfo("Hello World!");
                    }
                });

        .. group-tab:: Groovy

            Extensions have not yet been created for the Groovy helper libraries.


Raw API
=======

    The following example shows how to create a rule and triggers using the raw API without any support from the helper libraries.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from org.slf4j import LoggerFactory

                scriptExtension.importPreset("RuleSupport")
                scriptExtension.importPreset("RuleSimple")

                class GenericCronTriggerRawAPI(SimpleRule):
                    def __init__(self):
                        self.triggers = [
                            TriggerBuilder.create()
                                    .withId("Hello_World_Cron_Trigger")# no spaces allowed in trigger ID
                                    .withTypeUID("timer.GenericCronTrigger")
                                    .withConfiguration(
                                        Configuration({
                                            "cronExpression": "0/10 * * * * ?"
                                        })).build(),
                            TriggerBuilder.create()
                                    .withId("Hello_World_Item_State_Trigger")# no spaces allowed in trigger ID
                                    .withTypeUID("timer.GenericCronTrigger")
                                    .withConfiguration(
                                        Configuration({
                                            "itemName": "Test_Switch_1"
                                        })).build()
                        ]
                        self.name = "Jython Hello World (GenericCronTrigger raw API)"
                        self.description = "This is an example Jython cron rule using the raw API"
                        self.tags = set("Example rule tag")
                        self.log = LoggerFactory.getLogger("jsr223.jython.Hello World (GenericCronTrigger raw API)")

                    def execute(self, module, inputs):
                        self.log.info("Hello World!")

                automationManager.addRule(GenericCronTriggerRawAPI())

        .. group-tab:: JavaScript

            .. code-block:: JavaScript

                'use strict';

                scriptExtension.importPreset("RuleSupport");
                scriptExtension.importPreset("RuleSimple");

                var sRule = new SimpleRule() {
                    log: Java.type("org.slf4j.LoggerFactory").getLogger("jsr223.javascript.example"),
                    execute: function( module, inputs) {
                        this.log.info("Hello World!");
                    }
                };

                sRule.setTriggers([
                    TriggerBuilder.create()
                        .withId("aTimerTrigger")
                        .withTypeUID("timer.GenericCronTrigger")
                        .withConfiguration(
                            new Configuration({
                                "cronExpression": "0/10 * * * * ?"
                            })).build()
                    ]);

                sRule.name = "JavaScript Hello World example (raw API)";
                sRule.description = "This is an example Hello World rule using the raw API";
                automationManager.addRule(sRule);

        .. group-tab:: Groovy

            .. code-block:: Groovy

                import org.slf4j.LoggerFactory

                def log = LoggerFactory.getLogger("jsr223.groovy")

                import org.openhab.core.automation.Action
                import org.openhab.core.automation.module.script.rulesupport.shared.simple.SimpleRule
                import org.eclipse.smarthome.config.core.Configuration

                scriptExtension.importPreset("RuleSupport")

                def rawAPIRule = new SimpleRule() {
                    String name = "Groovy Hello World (GenericCronTrigger raw API)"
                    Object execute(Action module, Map<String, ?> inputs) {
                        log.info("Hello World!")
                    }
                }

                rawAPIRule.setTriggers([
                    TriggerBuilder.create()
                        .withId("aTimerTrigger")
                        .withTypeUID("timer.GenericCronTrigger")
                        .withConfiguration(new Configuration([cronExpression: "0/10 * * * * ?"]))
                        .build()
                    ])
                    
                automationManager.addRule(rawAPIRule)
