*****
Rules
*****

One of the primary use cases for JSR223 scripting in openHAB is to define rules for the `Next-Generation Rule Engine`_ using the `Automation API`_. 
The rule engine structures rules with *Modules* (Triggers, Conditions, Actions).
Modules are further broken down into *ModuleTypes* with cooresponding *ModuleHandlers*.
Scripted rules can use ModuleTypes that are already present in openHAB, and also define new ones that can be used outside of the scripting language that defined it, including rules created in the UI.

.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _Automation API: http://www.eclipse.org/smarthome/documentation/features/rules.html#java-api

In increasing order of complexity, rules can be written using the :ref:`How Tos/Rules:Decorators`, :ref:`How Tos/Rules:Extensions`, or the :ref:`How Tos/Rules:Raw API`.
The details for all of these methods are included here for reference, but the section on :ref:`How Tos/Rules:Decorators` should be all that is needed for creating your rules.
The decorators are abstractions (simplifications) of the extensions, which are abstractions of the raw API.

.. warning::

    Take care in your choice of object names used in your rules, so as not to use one that is already included in the `default scope <https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required>`_.


Decorators
==========

The easiest way to write rules, and the most familiar if you have used the openHAB rules DSL, is using the decorators provided by this library. 
Function decorators are part of the Python language and allow you to modify a function, to "decorate" it, using another function. 
The libraries provide a decorator called ``rule`` for defining rules and another called ``when`` for adding triggers to rules. 
This section will show you how to define rules and triggers, and it will also compare their usage with the syntax of the rules DSL to help with migration.


Imports
-------

    When writing rules with the decorators, you must import the decorator functions.
    This only needs to be done once at the top of each script you will be using them in.
    Two simple lines at the top of your file will accomplish this:

    .. tabs::

        .. group-tab:: Python

            .. code-block:: python

                from core.rules import rule
                from core.triggers import when

        .. group-tab:: Javascript

            Decorators have not yet been created for the Javascript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            The rules DSL does not require imports for creating rules or triggers.


@rule
-----

    The first step to creating a decorated rule is to give it a name that is unique in your openHAB configuration, and optionally a description and tags:
    The optional ``description`` allows for more detail about what a rule does and is displayed in the UI.
    The ``tags`` list is also optional, and useful for categorizing rules to simplifying searches. 

    .. tabs::

        .. group-tab:: Python
    
            .. code-block:: python

                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])

        .. group-tab:: Javascript

            Decorators have not yet been created for the Javascript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

              rule "Rule Name"
                  "Rule Description"


@when
-----

    Next we need to add triggers to the rule using the ``when`` decorator. 
    You may add as many or as few triggers as you want.
    Technically, you don't have to add any, but your rule will never be triggered if you don't. 
    ``@when`` must always follow ``@rule``, when writing rules. 
    The syntax for ``when`` is quite simple:

    .. tabs::

        .. group-tab:: Python
    
            .. code-block:: python
            
                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Item my_item changed to ON")

        .. group-tab:: Javascript

            Decorators have not yet been created for the Javascript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: java

                rule "Rule Name"
                when
                    Item my_item changed to ON

    The full list of triggers and details on each one can be found on the
    :doc:`../How Tos/Triggers` page.


Function
--------

    Finally the last piece is the actual code of your rule, which is a function.
    The name of this function must be unique within the file it is in. 
    It must be able to accept one positional argument, which will always be ``event`` in this documentation.

    The rule decorator adds some helpful attributes to the function.
    The rule UID is useful when enabling/disabling rules, ``my_rule_function.UID``.
    A logger is also provided for each rule, ``my_rule_function.log.info("Log message")``, and it will use the logger ``<core.logging.LOG_PREFIX>.Rule_Name``.
    More information on logging can be found on the :doc:`../How Tos/Logging` page.

    .. tabs::

        .. group-tab:: Python

            .. code-block:: python
            
                @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
                @when("Item my_item changed to ON")
                def my_rule_function(event):
                    # your Python code here

        .. group-tab:: Javascript

            Decorators have not yet been created for the Javascript helper libraries.

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

TODO

Raw API
=======

TODO
