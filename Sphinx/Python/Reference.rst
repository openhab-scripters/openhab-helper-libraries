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

It's important to understand the distinction between ``scripts`` and ``modules`` in regards to openHAB scripted automation.
A Python script is loaded by the ``javax.script`` (formerly known as JSR223) script engine manager that is integrated into the Next-Generation Rule Engine.
Each time a script file is loaded, openHAB creates an execution context for that script.
When the file is modified, openHAB will destroy the old script context and create a new one.
This means any objects (variables, classes, etc.) previously defined in the script will be lost when the script is reloaded.

A module is loaded by the Jython interpreter through the standard Python ``import`` directive which utilizes ``sys.path``.
Python module loading behavior applies, which means the module is normally loaded only once, and is not reloaded when the module source code changes.


Modifying and Reloading Packages or Modules
===========================================

Changes to a package or module will not take effect until all other packages, modules and scripts that have imported it have been reloaded.
Restarting openHAB will remedy this, but another option is to use the ``reload`` function.
Import the package or module, reload it, then import again.

Reload a package:

.. code-block:: python

    import personal.my_package
    reload(personal.my_package)
    import personal.my_package

Reload a module:

.. code-block:: python

    import personal.my_package.my_module
    reload(personal.my_package.my_module)
    import personal.my_package.my_module

If you are using an import like ``from personal.my_package.my_module import my_function``:

.. code-block:: python

    import personal.my_package.my_module
    reload(personal.my_package.my_module)
    from personal.my_package.my_module import my_function

In some cases, you may need to use this alternative:

.. code-block:: python

    import sys
    import community.my_package.my_module
    reload(sys.modules['community.my_package.my_module'])
    from community.my_package.my_module import my_function


Custom Packages and Modules
===========================

Custom modules and packages should be placed in ``/automation/lib/python/personal/``.
Modules do not have the same scope as scripts, but this can be remedied by importing ``scope`` from the ``jsr223`` module.
This will allow for things like accessing the itemRegistry:

.. code-block:: python

    from core.jsr223 import scope
    scope.itemRegistry.getItem("my_item")


Package and Module Locations
============================

One of the benefits of Jython over the openHAB rule DSL scripts is that you can use the full power of Python packages and modules to structure your code into reusable components.
After following the installation steps, these modules will be located in ``/automation/lib/python/``.
They can be located anywhere, but the Python path must be configured to find them.
There are several ways to do this:

#. Append the path to the ``python.path`` used in the EXTRA_JAVA_OPTS, separated with a colon in Linux and a semicolon in Windows, e.g. ``-Dpython.path=mypath1:mypath2``.
#. In your Python script, append the path to your package or module to the ``sys.path``:

    .. code-block:: python

        import sys
        sys.path.append("/path/to/my_package_or_module")

#. Add a symlink in ``/automation/lib/python/personal/``, which is already in the Python path, to the package or module.
