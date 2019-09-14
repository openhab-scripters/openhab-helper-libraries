=======================
Troubleshooting and FAQ
=======================

Table of Contents
=================

* `ideAlarm Troubleshooting and FAQ <ideAlarm Troubleshooting and FAQ>`

    * :ref:`Table of Contents <Python/Community/IdeAlarm/Troubleshooting:Table of Contents>`
    * :ref:`FAQ <Python/Community/IdeAlarm/Troubleshooting:FAQ>`
    * :ref:`Troubleshooting <Python/Community/IdeAlarm/Troubleshooting:Troubleshooting>`


FAQ
---

**How do I reset the alarm Zone status after an alert?**

Just toggle one of the 2 arming mode toggle switches that you have defined for your alarm zone.
That will disarm the zone and it will also reset the zone's status to "Normal".
Sirens will be switched off automatically.

**Will I get discount on my home insurance if I use ideAlarm?**

No.
IdeAlarm will never be graded and as such won’t meet the requirements of home insurance companies.
It won’t allow to become a professionally monitored security system.
On the other hand, you don't have to pay for monthly monitoring to a surveillance company.
No expenses for maintenance contracts.

**How can I improve the security of ideAlarm**

Get an UPS to your openHAB hardware.
An intruder might cut or simply turn off the mains power.

**I believe I've found a bug**

Please open an issue.
In order to be able to help you and to give you the best support, please include the following information:

* Copy the text from your configuration file.
  Use a code block, please.
* Set the logging level to DEBUG.
* Make the error occur and copy the relevant text from the openHAB log to your issue report.
  Use a code block, please.
* If relevant, describe how to reproduce the problem reported.


Troubleshooting
---------------

* Check that other Jython scripts run fine.
  Reread the :ref:`installation guide <Getting Started/Installation:Installation>` and follow the instructions to verify that the ``hello_world.py`` script functions.
* Check that you have the latest version of the openHAB Helper Libraries.
  If you just upgraded from an earlier version, check again that you made the necessary steps according to the :ref:`Release Notices <Python/Community/ideAlarm:Release Notices>`.
* Check your ``configuration.py`` and make sure that it's valid Python syntax.
