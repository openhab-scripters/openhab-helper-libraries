************
Installation
************

Since the ESH automation API is still under development, it is best to use a
current testing or snapshot release of openHAB. More importantly, there are
breaking changes in the API, so at least OH 2.4 snapshot 1319 or milestone M3
is required to use these modules.
**The ESH integration into the openHAB core has broken the JSR223 scripting
automation -- we are in the process of updating openHAB and this library to
work post-integration**

| Given that the automation API and this library are still under development, it
  is highly recommended to turn on debug logging. This can be done using the
  following command in the Karaf console:
  ``log:set DEBUG org.eclipse.smarthome.automation``
| Once your installation and scripts are tested and working, you may wish to
  reduce the log level to warn to reduce the amount of log entries. This can be
  done using the following command in Karaf:
  ``log:set WARN org.eclipse.smarthome.automation``



Package Install
===============

If you installed openHAB with your distro's package manager or are using
openHABian, these instructions are for you!

1. Install the `Experimental Rule Engine`_ add-on
2. Turn on debug logging using
   ``log:set DEBUG org.eclipse.smarthome.automation`` in the Karaf console
3. Shutdown openHAB
4. Download the contents of this repository and, using the openHAB account,
   copy the contents of the ``/Core/`` directory into ``/etc/openhab2/``.
   This will create a directory structure as described in File Locations, and
   will include all of the Core files, including a startup delay script that
   insures OH is started completely before loading other scripts.
5. Download the `standalone Jython 2.7.0 jar`_ and copy it to
   ``/etc/openhab2/automation/jython/``.
6. Add/modify your ``EXTRA_JAVA_OPTS`` in ``/etc/default/openhab2`` to include
   the following:

   .. code-block:: bash

     EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"

   *If creating a new file, remember to set the permissions so that the OH
   account has read access.*

7. Copy the ``/Script Examples/hello_world.py`` script to
   ``/automation/jsr223/personal/`` to test if everything is working.
   This script will make a log entry every 10s, and should be deleted after
   installation has been verified.
8. Start openHAB and watch the logs for errors and the entries from the
   ``hello_world.py`` script.

Check out the :doc:`getting-started` page for what to do next.


Manual Install
==============

If you installed openHAB manually, these instructions are for you!

1. Install the `Experimental Rule Engine`_ add-on
2. Turn on debug logging using
   ``log:set DEBUG org.eclipse.smarthome.automation`` in the Karaf console
3. Shutdown openHAB
4. Download the contents of this repository and, using the openHAB account,
   copy the contents of the ``/Core/`` directory into ``/opt/openhab2/conf/``.
   This will create a directory structure as described in File Locations, and
   will include all of the Core files, including a startup delay script that
   insures OH is started completely before loading other scripts.
5. Download the `standalone Jython 2.7.0 jar`_ and copy it to
   ``/opt/openhab2/conf/automation/jython/``.
6. Add/modify your ``EXTRA_JAVA_OPTS`` in ``/opt/openhab2/start.sh`` to include
   the following:

   .. code-block:: bash

     export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"

   *If creating a new file, remember to set the permissions so that the OH
   account has read access.*

7. Copy the ``/Script Examples/hello_world.py`` script to
   ``/automation/jsr223/personal/`` to test if everything is working.
   This script will make a log entry every 10s, and should be deleted after
   installation has been verified.
8. Start openHAB and watch the logs for errors and the entries from the
   ``hello_world.py`` script.

Check out the :doc:`getting-started` page for what to do next.


Docker
======

do else


.. _Experimental Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _standalone Jython 2.7.0 jar: http://www.jython.org/downloads.html
