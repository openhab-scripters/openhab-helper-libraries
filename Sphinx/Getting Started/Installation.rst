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
    There is a main configuration file for each scripting language's helper libraries that will need to be renamed.

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

.. |jython_other_verions| replace::
    A full installation of Jython can also be used, but the paths above would need to be modified.
    Jython 2.7.1 and 2.7.2a1+ will also work, but 2.7.0 has proven to be very stable.

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
        #. Add/modify the Python registry file.
           These examples assume that you will be using the standalone Jython 2.7.0 jar in the next step.

           .. tabs::

               .. group-tab:: Package Install

                   The paths shown here are for Linux package repository openHAB installations, including openHABian.

                   Edit the file ``/usr/share/openhab2/runtime/lib/ext/registry`` using your preferred text editor,
                   making directories as needed.

                   If creating a new file, remember to set the permissions so that the ``openhab`` account has at least read access.
                   If a file already exists and there is a ``python.path`` variable, add a semi-colon and append the following.

                   .. code-block:: Text

                       python.path=/etc/openhab2/automation/lib/python

               .. group-tab:: Manual Install

                   The paths shown here are the defaults for manual openHAB installations on Linux.

                   Edit the file ``/opt/openhab2/runtime/lib/ext/registry`` using your preferred text editor,
                   making directories as needed.

                   If creating a new file, remember to set the permissions so that the ``openhab`` account has at least read access.
                   If a file already exists and there is a ``python.path`` variable, add a semi-colon and append the following.

                   .. code-block:: Text

                       python.path=/opt/openhab2/conf/automation/lib/python

               .. group-tab:: Windows Install

                   The paths shown here are examples for Windows openHAB installations.

                   Edit the file ``C:\openhab2\runtime\lib\ext\registry`` using your preferred text editor,
                   making directories as needed.

                   If a file already exists and there is a ``python.path`` variable, add a semi-colon and append the following.

                   .. code-block:: Text

                       python.path=C:\openhab2\conf\automation\lib\python

        #. .. tabs::

               .. group-tab:: Package Install

                   Download the `standalone Jython 2.7.0 jar <http://www.jython.org/downloads.html>`_ and copy it to
                   ``/usr/share/openhab2/runtime/lib/ext/``

                   |jython_other_verions|

               .. group-tab:: Manual Install

                   Download the `standalone Jython 2.7.0 jar <http://www.jython.org/downloads.html>`_ and copy it to
                   ``/opt/openhab2/runtime/lib/ext/``

                   |jython_other_verions|

               .. group-tab:: Windows Install

                   Download the `standalone Jython 2.7.0 jar <http://www.jython.org/downloads.html>`_ and copy it to
                   ``C:\openhab2\runtime\lib\ext\``

                   |jython_other_verions|

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
