*****************
Setting up VSCode
*****************

The following steps will configure Visual Studio Code to recognize the Helper Libraries
and provide examples of how to reduce the number of errors being displayed because VSCode
does not have access to any openHAB packages.

ENV File
========

    Create a ``.env`` file in the root of your openHAB conf directory (ex ``{OH_CONF}/.env``)
    and add the following to it:

    .. code-block:: Text

        PYTHONPATH="./automation/lib/python"

    This will allow ``pylint`` to see any packages or modules in that directory and no longer
    show import errors for them.

``.pylintrc`` File
==================

    Copy the ``OHCONF.pylintrc`` file from the root of this repository into your openHAB conf
    directory and rename it to ``.pylintrc``. It will prevent any openHAB or Java packages from
    being listed as missing, as well as all objects from the Default Preset.

    [``OHCONF.pylintrc``](https://github.com/openhab-scripters/openhab-helper-libraries/blob/master/.gitignore)
