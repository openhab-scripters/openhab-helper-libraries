*****************
Setting up VSCode
*****************

The following steps will configure Visual Studio Code to recognize the Helper Libraries
and provide examples of how to reduce the number of errors being displayed because VSCode
does not have access to any openHAB packages.

Python Version 
========

    Install Python 2.7 on the computer that Visual Studio Code is running on. Select version Python 
    version 2.7 in VS Code (bottom left corner of the VS Code window).

ENV File
========

    Create a ``.env`` file in the root of your openHAB conf directory (ex ``{OH_CONF}/.env``)
    and add the following to it:

    .. code-block:: Text

        PYTHONPATH="./automation/lib/python"

    This will allow ``pylint`` to see any packages or modules in that directory and no longer
    show import errors for them.

Exclude Helper Libraries
========================

    If you don't already have an ``{OH_CONF}/.vscode/settings.json`` file, create it and
    add the following:

    .. code-block:: JSON

        {
            "python.linting.ignorePatterns": [
                "**/automation/**/python/core/**/*.py",
                "**/automation/**/python/community/**/*.py"
            ]
        }

    This will tell ``pylint`` to ignore all files in the Helper Libraries' ``core`` and
    ``community`` directories, greatly reducing the number of errors you will see
    because of openHAB packages it cannot import.

pylint Directives
=================

    Lastly, you can use ``pylint`` directives if you want to disable the import error
    messages in your files for the openHAB packages that it cannot import.

    When importing packages or classes from openHAB:

    .. code-block::

        # pylint: disable=import-error
        from org.openhab.core.library.items import SwitchItem
        # pylint: enable=import-error

    When importing ``scope`` from ``core.jsr223``:

    .. code-block::

        # pylint: disable=import-error, no-name-in-module
        from core.jsr223 import scope
        # pylint: enable=import-error, no-name-in-module
