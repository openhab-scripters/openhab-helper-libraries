*********
Reference
*********

Suggested reading
=================

* https://www.jython.org/jythonbook/en/1.0/index.html
* https://wiki.python.org/moin/BeginnersGuide
* https://docs.python.org/2/

Scripts vs. Modules
===================

It's important to understand the distinction between Jython ``scripts`` and ``modules`` in regards to openhab scripted automation.
A Jython script is loaded by the `javax.script` script engine manager (formerly known as JSR223) that is integrated into the Next-Generation Rule Engine within openHAB Core.
Each time a script file is loaded, openHAB creates an execution context for that script.
When the file is modified, openHAB will destroy the old script context and create a new one.
This means any objects (variables, classes, etc.) previously defined in the script will be lost when the script is reloaded.

A Jython module is loaded by Jython itself through the standard Python `import` directive and uses `sys.path`.
The normal Python module loading behavior applies.
This means the module is normally loaded only once, and is not reloaded when the module source code changes.


Modifying/Reloading Modules
===========================

Changes to a module will not take effect until all other modules and scripts that have imported it have been reloaded.
Restarting openHAB will remedy this, but another option is to use the reload() function:

.. code-block:: python

    import myModule
    reload(myModule)
    import myModule

If using imports like `from core.triggers import when`, or if the module is in a package, you will need to use:

.. code-block:: python

    import core.triggers
    reload(core.triggers)
    from core.triggers import when

Alternatively...

.. code-block:: python

    import sys
    from core.triggers import when
    reload(sys.modules['core.triggers'])
    from core.triggers import when


Custom Modules
==============

Custom modules and packages should be placed in ``/automation/lib/python/personal/``.
Modules do not have the same scope as scripts, but this can be remedied by importing ``scope`` from the ``jsr223`` module.
This will allow for things like accessing the itemRegistry:

.. code-block:: python

    from core.jsr223 import scope
    scope.itemRegistry.getItem("MyItem")


Module Locations
================

One of the benefits of Jython over the openHAB rule DSL scripts is that you can use the full power of Python packages and modules to structure your code into reusable components.
After following the installation steps, these modules will be located in ``/automation/lib/python/``.
They can be located anywhere, but the Python path must be configured to find them.
There are several ways to do this:

#. Append the path to the ``python.path`` used in the EXTRA_JAVA_OPTS, separated woth a colon in Linux and a semicolon in Windows, e.g. ``-Dpython.path=mypath1:mypath2``.
#. Modify the ``sys.path`` list in a Jython script that loads early (like a component script).
#. Add a symlink in ``/automation/lib/python/personal/``, which is already in the Python path, to the module or a package that contains it.
