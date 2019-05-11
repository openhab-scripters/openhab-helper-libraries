*****
Rules
*****

One of the primary use cases for JSR223 scripting in OH is to define rules for
the `Eclipse Smarthome rule engine`_ using the `Java Automation API`_. The ESH
rule engine structures rules as *Modules* (Triggers, Conditions, Actions).
Jython rules can use rule Modules that are already present in ESH, and can
define new Modules that can be used outside of JSR223 scripting. Take care not
to confuse ESH Modules with Jython modules.

.. _Eclipse Smarthome rule engine: http://www.eclipse.org/smarthome/documentation/features/rules.html
.. _Java Automation API: http://www.eclipse.org/smarthome/documentation/features/rules.html#java-api

In increasing order of complexity, rules can be written using the :ref:`How Tos/Rules:Decorators`,
Jython :ref:`How Tos/Rules:Extensions`, or the raw :ref:`How Tos/Rules:Automation API`.
The details for all of these methods are included here for reference, but the
section on :ref:`How Tos/Rules:Decorators` should be all that is needed for
creating your rules.

.. warning::

  Take care in your choice of object names used in your rules, so as not to use
  one that is already included in the `default scope <https://www.openhab.org/docs/configuration/jsr223.html#default-variables-no-preset-loading-required>`_.


Decorators
==========

  The easiest way to write rules, and most familiar if you have used the openHAB
  DSL, is using the decorators provided by this library. Function decorators
  are part of the Python language and allow you to modify a function, to
  "decorate" it, using another function. This library provides a decorator
  called ``rule`` for defining rules, and another called ``when`` for adding
  triggers to rules. This section will show you how to define rules and
  triggers, and will compare to the syntax of the Rules DSL to help with
  migration.

Import
------

    When writing rules with the decorators you must import the decorator
    functions, this only needs to be done once at the top of each file you will
    be using them in.
    Two simple lines at the top of your file will accomplish this:

    .. code-block::

      from core.rules import rule
      from core.triggers import when

@rule
-----

    The first step to creating a rule is to give it a name that is unique in
    your openHAB configuration, and optionally a description and tags, using
    the ``rule`` decorator like this:

    .. code-block::

      @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])

    The ``description`` is optional and allows for more detail about what a rule
    does. The ``tags`` list is also optional, tags are used to help categorize
    and search rules in the UI.

    In the openHAB Rules DSL this is equivilent of:

    .. code-block:: java

      rule "Rule Name"
          "Rule Description"

@when
-----

    Next we need to add triggers to the rule using the ``when`` decorator. You
    may add as many or as few triggers as you want, technically you don't have to
    add any but your rule will never be triggered if you don't. ``@when`` must
    always follow ``@rule`` when writing rules. The syntax for ``when`` is quite
    simple:

    .. code-block::
    
      @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
      @when("Item my_item changed to ON")

    That's all there is to it! In the Rules DSL this looks like:

    .. code-block:: java

      rule "Rule Name"
          "Rule Description"
      when
          Item my_item changed to ON

    The full list of triggers and details on each one can be found on the
    :doc:`/How Tos/Triggers` page.

Function
--------

    Finally the last piece is the actual code of your rule, which is a function.
    The name of this function must be unique within the file it is in. It must
    be able to accept 1 positional argument, which will always be ``event`` in
    this documentation.

    .. code-block::
    
      @rule("Rule Name", description="Optional Rule Description", tag=["Tag 1", "Tag 2"])
      @when("Item my_item changed to ON")
      def my_rule_function(event):
          # your Python code here

    | The rule UID is available as an attribute of the rule if you need it:
    | ``my_rule_function.UID``
    
    | A logger is also provided for each rule:
    | ``my_rule_function.log.info("Log message")``
    | Which logs to:
    | ``<core.logging.LOG_PREFIX>.Rule_Name``
    | More information on logging can be found on the :doc:`/How Tos/Logging` page.

    In the Rules DSL this looks like:

    .. code-block:: java

      rule "Rule Name"
          "Rule Description"
      when
          Item my_item changed to ON
      then
          // your DSL code here
      end


Extensions
==========

Automation API
==============