*****************
Quick Start Guide
*****************

.. tabs::

    .. group-tab:: Python

        1. |step1|
        2. |step2|
        3. |step3|
        4. |step4|
        5. |step5|
        6. |step6|
        7. |step7|
        8. |step8|
        9. |step9|
        10. |step10|
        11. |step11|
        12. |step12|
        13. |step13|

    .. group-tab:: JavaScript

        1. |step1|
        2. |step2|
        3. |step3|
        4. |step4|
        5. |step5|
        6. |step6|
        7. |step7|
        8. |step8|
        9. |step9|
        10. |step10|
        11. |step11|
        12. |step12|
        13. |step13|

    .. group-tab:: Groovy

        1. |step1|
        2. |step2|
        3. |step3|
        4. |step4|
        5. |step5|
        6. |step6|
        7. |step7|
        8. |step8|
        9. |step9|
        10. |step10|
        11. |step11|
        12. |step12|
        13. |step13|


.. |step1| replace:: The `Next-Generation Rule Engine`_ is still in development, so it is recommended to use the latest snapshot or milestone release of openHAB. 

.. |step2| replace:: Use the `Karaf logging`_ commands to enable debug logging for automation: 
    ``log:set DEBUG org.openhab.core.automation``
    Leave this on for setup and testing, but you may want to set to WARN when everything is setup. 
    For older openHAB builds before the ESH reintegration (older than snapshot 1566 and 2.5M2), you will need to changed this to `org.eclipse.smarthome.automation`. 

.. |step3| replace:: Enable debug logging for jsr223: 
    `log:set DEBUG jsr223`
    This is the default logger used in the examples and the helper libraries.

.. |step4| replace:: Review the general `openHAB JSR223 Scripting`_ and the language specific documentation found as links on that page. 

.. |step5| replace:: Install the `Next-Generation Rule Engine`_ add-on.

.. |step6| replace:: Shut down openHAB.

.. |step7| replace:: `Download the contents of this repository`_ and, using the openHAB account, copy the *contents* of the ``/Core/`` directory into: 
    - ``/etc/openhab2/`` (package repository OH install, like openHABian)
    - ``/opt/openhab2/conf/`` (default manual OH install).
    This will create a directory structure, as described in [File Locations](#File-Locations). 
    This will contain all of the Core files for each language, including the startup delay scripts that ensure OH has started completely before loading other scripts.
    If you do not plan to use all of the languages, you may want to remove the directories for them under `/automation/jsr223/` and `/automation/lib/`.

.. |step8| replace:: There is a main configuration file for each scripting language's helper libraries that will need to be renamed. 
    For example, in ``\automation\lib\python\``, rename the file ``configuration.py.example`` to ``configuration.py``.
    These files can be used to secure personal information, so that they are not stored in files that may be shared with the community, or to store variables that are accesed by multiple scripts and/or modules, e.g. LOG_PREFIX. 

.. |step9| replace:: For Jython, follow the steps in the [Getting Started](Python/Getting-Started.md#additional-setup-for-jython). For Groovy, follow the steps in the [Getting Started](Groovy/README.md#additional-setup-for-groovy). When complete, come back here. 

.. |step10| replace:: Copy the Hello World example script for the language(s) that you are using to the ``jsr223`` directory:
    - copy [`/Script Examples/Python/hello_world.py`](/Script%20Examples/Python/hello_world.py) to ``/automation/jsr223/python/personal/``
    - copy ['/Script Examples/Javascript/HelloWorld.js'](/Script%20Examples/Javascript/HelloWorld.js) to ``/automation/jsr223/javascript/personal/``)
    - copy ['/Script Examples/Groovy/HelloWorld.groovy'](/Script%20Examples/Groovy/HelloWorld.groovy) to ``/automation/jsr223/groovy/personal/``)

.. |step11| replace:: Start openHAB and watch the logs for errors and the entries from the Hello World script.
    This script will make a log entry every 10s, and should be deleted after installation has been verified.

.. |step12| replace:: Review the language specific helper library documentation: 
    - [Groovy](Groovy/README.md)
    - [Javascript](Javascript/README.md)
    - [Jython (Python)](Python/README.md)

.. |step13| replace:: Ask questions on the `openHAB forum`_ and tag posts with ``jsr223``. Report issues `here`_, but please don't hesitate to update the documentation and code.
    Just like openHAB, this repository is community driven!


.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _Karaf logging: https://www.openhab.org/docs/administration/logging.html
.. _openHAB JSR223 Scripting: https://www.openhab.org/docs/configuration/jsr223.html
.. _Download the contents of this repository: https://github.com/openhab-scripters/openhab-helper-libraries/archive/master.zip
.. _openHAB forum: https://community.openhab.org/tags/jsr223
.. _here: https://github.com/openhab-scripters/openhab-helper-libraries/issues