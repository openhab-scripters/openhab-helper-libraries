************
Installation
************

Core
====

.. toctree::
    :hidden:
    :maxdepth: 0

    Docker.rst

Instructions for installation in a Docker container are available :doc:`here <Docker>`.

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

.. |core_step_1| replace::
    The `Next-Generation Rule Engine`_ is still in development, so it is recommended to use the latest snapshot or milestone release of `openHAB`_.

.. |core_step_2| replace::
    Use the `Karaf logging`_ commands to enable debug logging for automation: ``log:set DEBUG org.openhab.core.automation``.
    Leave this on for setup and testing, but you may want to set to WARN when everything is setup.
    For older openHAB builds before the ESH reintegration (older than snapshot 1566 and 2.5M2), you will need to change this to ``org.eclipse.smarthome.automation``.

.. |core_step_3| replace::
    Enable debug logging for jsr223: ``log:set DEBUG jsr223``.
    This is the default logger used in the examples and the helper libraries.

.. |core_step_4| replace::
    Review the general `openHAB Scripted Automation documentation`_ and the language specific documentation found as links on that page.

.. |core_step_5| replace::
    Install the `Next-Generation Rule Engine`_ add-on.

.. |core_step_6| replace::
    Shut down openHAB.

.. |core_step_7| replace::
    `Download the contents of this repository`_.
    Using the ``openhab`` account, copy the *contents* of the ``/Core/`` directory into your openHAB's site configuration directory (`Linux`_, `Windows`_).
    This will create a directory structure as described in :doc:`File Locations` and will contain all of the Core files for each language, including the startup delay scripts that ensure openHAB has started completely before loading other scripts.
    If you do not plan to use all of the languages, you may want to remove the directories for them under ``/automation/jsr223/`` and ``/automation/lib/``.

.. |core_step_8a| replace::
    There is a main configuration file for each scripting language's helper libraries that must be renamed.

.. |core_step_8b| replace::
    These files can be used to secure personal information, so that they are not stored in files that may be shared with the community, or to store variables that are accesed by multiple scripts and/or modules, e.g. LOG_PREFIX.

.. |core_step_9| replace::
    Start openHAB and watch the logs for errors and the entries from the Hello World script.
    This script will make a log entry every 10s and should be deleted after installation has been verified.

.. |core_step_10| replace::
    Ask questions on the `openHAB forum`_ and tag posts with ``jsr223``. Report issues `here`_, but please don't hesitate to update the documentation and code.
    Just like openHAB, this repository is community driven!

.. |core_step_11| replace::
    Check out the :doc:`First Steps` page for what to do next.

.. tabs::

    .. group-tab:: Python

        #. |core_step_1|
        #. |core_step_2|
        #. |core_step_3|
        #. |core_step_4|
        #. |core_step_5|
        #. |core_step_6|
        #. |core_step_7|
        #. |core_step_8a|
           For example, in ``/automation/lib/python/``, rename the file ``configuration.py.example`` to ``configuration.py``.
           |core_step_8b|
        #. The ''/automation/lib/python/personal/__init.py.example`` file must be renamed to ``__init__.py``.
           If you modify it, take care not to overwrite the file during upgrades.
        #. Add/modify the EXTRA_JAVA_OPTS.
           These examples assume that you will be using the standalone Jython 2.7.0 jar in the next step.
           Changes to the EXTRA_JAVA_OPTS require an openHAB restart.

           .. tabs::

               .. group-tab:: Using an ``/etc/default/openhab2`` file

                   This option is typically used with a package repository openHAB installation (includes openHABian).
                   If creating a new file, remember to set the permissions so that the `openhab` account has at least read access.
                   If a file already exists and there is an EXTRA_JAVA_OPTS variable, add a space and append everything in quotes.

                   .. code-block:: none

                       EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"

               .. group-tab:: Using the ``start.sh`` script

                   This option is typically used with a manual openHAB installation on Linux.

                   .. code-block:: none

                       # Add to the top of the file
                       export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"

               .. group-tab:: Using the ``start.bat`` script

                   This option is for a manual openHAB installation on Windows.
                   If you are *not* using OH 2.5, 2.5M2, S1604, or newer, you will first need to update your ``C:\openhab2\runtime\bin\setenv.bat`` file with the `changes in the current file <https://github.com/openhab/openhab-distro/blob/master/distributions/openhab/src/main/resources/bin/setenv.bat#L121>`_.

                   .. code-block:: none

                       REM Add to the top of the file
                       set EXTRA_JAVA_OPTS=-Xbootclasspath/a:C:\openhab2\conf\automation\jython\jython-standalone-2.7.0.jar -Dpython.home=C:\openhab2\conf\automation\jython -Dpython.path=C:\openhab2\conf\automation\lib\python

        #. Download the `standalone Jython 2.7.0 jar <http://www.jython.org/downloads.html>`_ and copy it to the path specified above in the EXTRA_JAVA_OPTS.
           A full installation of Jython can also be used, but the paths above would need to be modified.
           Jython 2.7.1 and 2.7.2a1+ will also work, but 2.7.0 has proven to be very stable.
        #. Copy the ``/Script Examples/Python/hello_world.py`` script to ``/automation/jsr223/python/personal/``.
        #. |core_step_9|
        #. |core_step_10|
        #. |core_step_11|

    .. group-tab:: JavaScript

        #. |core_step_1|
        #. |core_step_2|
        #. |core_step_3|
        #. |core_step_4|
        #. |core_step_5|
        #. |core_step_6|
        #. |core_step_7|
        #. |core_step_8a|
           For example, in ``/automation/lib/javascript/``, rename the file ``configuration.js.example`` to ``configuration.js``.
           |core_step_8b|
        #. Copy the ``/Script Examples/Javascript/HelloWorld.js`` script to ``/automation/jsr223/javascript/personal/``.
        #. |core_step_9|
        #. |core_step_10|
        #. |core_step_11|

    .. group-tab:: Groovy

        #. |core_step_1|
        #. |core_step_2|
        #. |core_step_3|
        #. |core_step_4|
        #. |core_step_5|
        #. |core_step_6|
        #. |core_step_7|
        #. |core_step_8a|
           For example, in ``/automation/lib/groovy/``, rename the file ``configuration.groovy.example`` to ``configuration.groovy``.
           |core_step_8b|
        #. Download the `Groovy binary`_.
        #. Extract ``/groovy-2.4.12/lib/groovy*.jar`` to ``/runtime/lib/ext/``.
        #. Copy the ``/Script Examples/Groovy/HelloWorld.groovy`` script to ``/automation/jsr223/groovy/personal/``.
        #. |core_step_9|
        #. |core_step_10|
        #. |core_step_11|

Update/Upgrade
=========
To upgrade to the latest version of the helper libraries, delete the older version and follow the installation steps.


Community
=========

The Community section of the repository contains scripts and libraries that contain functionality beyond what is provided in Core.
For the scripting language(s) being used, browse the Community documentation and/or the files downloaded from the repository.
These instructions will help guide you through process of installing or upgrading a Community package.

.. |community_step_1| replace::
    Locate the directory containing the Community package that you'd like to install.

.. |community_step_2| replace::
    Copy it's *contents* into your openHAB configuration directory, similar to how Core was installed in step 7 above.

.. |community_step_3| replace::
    There may be some files that will need to be manually edited, so check the instructions for the Community package.

.. |community_step_4| replace::
    When updating a Community package that contains libraries which have changed, openHAB will need to be restarted for the changes to take effect.

.. tabs::

    .. group-tab:: Python

        #. |community_step_1|
        #. |community_step_2|
        #. |community_step_3|
           For example, there may be some settings copied to ``/automation/lib/python/configuration.py.example`` that need to be added to ``configuration.py``.
        #. |community_step_4|
           If using Python, you could alternatively use the methods described in :ref:`Python/Reference:Modifying and Reloading Packages or Modules`.

    .. group-tab:: JavaScript

        #. |community_step_1|
        #. |community_step_2|
        #. |community_step_3|
           For example, there may be some settings copied to ``/automation/lib/javascript/configuration.js.example`` that need to be added to ``configuration.js``.
        #. |community_step_4|

    .. group-tab:: Groovy

        #. |community_step_1|
        #. |community_step_2|
        #. |community_step_3|
           For example, there may be some settings copied to ``/automation/lib/python/configuration.groovy.example`` that need to be added to ``configuration.groovy``.
        #. |community_step_4|


Personal
========

Personal scripts and modules should be placed in the appropriate ``personal`` directories documented in :doc:`File Locations`.
Once installed, the files in ``community`` and ``core`` directories should **not** be modified.
If you want to make or test a change, first copy the files to ``personal`` directories (you may also need to modify imports too).


.. _openHAB: https://www.openhab.org/download/
.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _openHAB Scripted Automation documentation: https://www.openhab.org/docs/configuration/jsr223.html
.. _Karaf logging: https://www.openhab.org/docs/administration/logging.html
.. _openHAB forum: https://community.openhab.org/tags/jsr223
.. _Download the contents of this repository: https://github.com/openhab-scripters/openhab-helper-libraries/archive/master.zip
.. _Linux: https://www.openhab.org/docs/installation/linux.html#file-locations
.. _Windows: https://www.openhab.org/docs/installation/windows.html#file-locations
.. _Groovy binary: https://dl.bintray.com/groovy/maven/apache-groovy-binary-2.4.12.zip
.. _here: https://github.com/openhab-scripters/openhab-helper-libraries/issues
