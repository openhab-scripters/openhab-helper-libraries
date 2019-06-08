************
Installation
************

.. toctree::
    :hidden:
    :maxdepth: 0

    Docker.rst

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. |step1| replace:: The `Next-Generation Rule Engine`_ is still in development, so it is recommended to use the latest snapshot or milestone release of `openHAB`_. 

.. |step2| replace:: Use the `Karaf logging`_ commands to enable debug logging for automation: ``log:set DEBUG org.openhab.core.automation``.
    Leave this on for setup and testing, but you may want to set to WARN when everything is setup.
    For older openHAB builds before the ESH reintegration (older than snapshot 1566 and 2.5M2), you will need to change this to `org.eclipse.smarthome.automation`.

.. |step3| replace:: Enable debug logging for jsr223: ``log:set DEBUG jsr223``. 
    This is the default logger used in the examples and the helper libraries.

.. |step4| replace:: Review the general `openHAB Scripted Automation documentation`_ and the language specific documentation found as links on that page. 

.. |step5| replace:: Install the `Next-Generation Rule Engine`_ add-on.

.. |step6| replace:: Shut down openHAB.

.. |step7| replace:: `Download the contents of this repository`_. Using the ``openhab`` account, copy the *contents* of the ``/Core/`` directory into: |br|
    * package repository openHAB installation, like openHABian: ``/etc/openhab2/`` |br|
    * default Linux manual openHAB installation: ``/opt/openhab2/conf/`` |br|
    * default Windows manual openHAB installation: ``C:\openhab2\conf\`` |br|
    This will create a directory structure as described in :doc:`../File Locations`. 
    This will contain all of the Core files for each language, including the startup delay scripts that ensure openHAB has started completely before loading other scripts.
    If you do not plan to use all of the languages, you may want to remove the directories for them under ``/automation/jsr223/`` and ``/automation/lib/``.

.. |step8a| replace:: There is a main configuration file for each scripting language's helper libraries that will need to be renamed. 
.. |step8b| replace:: These files can be used to secure personal information, so that they are not stored in files that may be shared with the community, or to store variables that are accesed by multiple scripts and/or modules, e.g. LOG_PREFIX. 

.. |step9| replace:: Start openHAB and watch the logs for errors and the entries from the Hello World script.
    This script will make a log entry every 10s and should be deleted after installation has been verified.

.. |step10| replace:: Ask questions on the `openHAB forum`_ and tag posts with ``jsr223``. Report issues `here`_, but please don't hesitate to update the documentation and code.
    Just like openHAB, this repository is community driven!

.. tabs::

    .. group-tab:: Python

        #.  |step1|
        #.  |step2|
        #.  |step3|
        #.  |step4|
        #.  |step5|
        #.  |step6|
        #.  |step7|
        #.  |step8a|
            For example, in ``/automation/lib/python/``, rename the file ``configuration.py.example`` to ``configuration.py``.
            |step8b|
        #.  Add/modify the EXTRA_JAVA_OPTS. 
            These examples assume that you will be using the standalone Jython 2.7.0 jar in the next step. 
            Changes to the EXTRA_JAVA_OPTS require an openHAB restart. 

            .. tabs::

                .. group-tab:: Using an `/etc/default/openhab2` file
                
                    This option is typically used with a package repository openHAB installation (includes openHABian).
                    If creating a new file, remember to set the permissions so that the `openhab` account has at least read access.
                    If a file already exists and there is an EXTRA_JAVA_OPTS variable, add a space and append everything in quotes.

                    .. code-block:: bash

                        EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"

                .. group-tab:: Using the `start.sh` script
                
                    This option is typically used with a manual openHAB installation on Linux.

                    .. code-block:: bash

                        # Add to the top of the file
                        export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"

                .. group-tab:: Using the `start.bat` script
                
                    This option is for a manual openHAB installation on Windows.
                    If you are *not* using OH 2.5, 2.5M2, S1604, or newer, you will first need to update your ``C:\openhab2\runtime\bin\setenv.bat`` file with the `changes in the current file <https://github.com/openhab/openhab-distro/blob/master/distributions/openhab/src/main/resources/bin/setenv.bat#L121>`_.

                    .. code-block:: bat

                        REM Add to the top of the file
                        set EXTRA_JAVA_OPTS=-Xbootclasspath/a:C:\openhab2\conf\automation\jython\jython-standalone-2.7.0.jar -Dpython.home=C:\openhab2\conf\automation\jython -Dpython.path=C:\openhab2\conf\automation\lib\python

        #.  Download the `standalone Jython 2.7.0 jar <http://www.jython.org/downloads.html>`_ and copy it to the path specified above in the EXTRA_JAVA_OPTS. 
            A full installation of Jython can also be used, but the paths above would need to be modified.
            Jython 2.7.1 and 2.7.2a1+ will also work, but 2.7.0 has proven to be very stable.
        #.  After completing the steps in the [Quick Start Guide](/Docs/README.md#quick-start-guide), create rules using [rule and trigger decorators](Defining-Rules.md#rule-and-trigger-decorators). 
            There is documentation on how to create rules directly with the API, but the decorators are by far the simplest.
        #.  Copy the ``/Script Examples/Python/hello_world.py`` script to ``/automation/jsr223/python/personal/``.
        #.  |step9|
        #.  Review the Jython helper library documentation.
        #.  |step10|

    .. group-tab:: JavaScript

        #.  |step1|
        #.  |step2|
        #.  |step3|
        #.  |step4|
        #.  |step5|
        #.  |step6|
        #.  |step7|
        #.  |step8a|
            For example, in ``/automation/lib/javascript/``, rename the file ``configuration.js.example`` to ``configuration.js``.
            |step8b|
        #.  Copy the ``/Script Examples/Javascript/HelloWorld.js`` script to ``/automation/jsr223/javascript/personal/``.
        #.  |step9|
        #.  Review the Javascript helper library documentation.
        #.  |step10|

    .. group-tab:: Groovy

        #.  |step1|
        #.  |step2|
        #.  |step3|
        #.  |step4|
        #.  |step5|
        #.  |step6|
        #.  |step7|
        #.  |step8a|
            For example, in ``/automation/lib/groovy/``, rename the file ``configuration.groovy.example`` to ``configuration.groovy``.
            |step8b|
        #.  Download the `Groovy binary`_. 
        #.  Extract ``/groovy-2.4.12/lib/groovy*.jar`` to ``/runtime/lib/ext/``. 
        #.  Copy the ``/Script Examples/Groovy/HelloWorld.groovy`` script to ``/automation/jsr223/groovy/personal/``.
        #.  |step9|
        #.  Review the Groovy helper library documentation.
        #.  |step10|


.. Docker
.. ======

.. There are also instructions for installation in a :doc:`Docker` container.


Check out the :doc:`../First Steps` page for what to do next.

.. _openHAB: https://www.openhab.org/download/
.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _openHAB Scripted Automation documentation: https://www.openhab.org/docs/configuration/jsr223.html
.. _Karaf logging: https://www.openhab.org/docs/administration/logging.html
.. _openHAB forum: https://community.openhab.org/tags/jsr223
.. _Download the contents of this repository: https://github.com/openhab-scripters/openhab-helper-libraries/archive/master.zip
.. _Groovy binary: https://dl.bintray.com/groovy/maven/apache-groovy-binary-2.4.12.zip
.. _here: https://github.com/openhab-scripters/openhab-helper-libraries/issues