**************
File Locations
**************

Example Directory Structure

.. code-block:: none

    └── etc/openhab2 or opt/openhab2/conf or C:\openhab2
        └── automation
            ├── jsr223
            │   ├── groovy
            │   │   ├── community
            │   │   │   └── something_from_the_community
            │   │   │       └── some_community_script.groovy
            │   │   ├── core
            │   │   │   ├── components
            │   │   │   └── 000_startup_delay.groovy
            │   │   └── personal
            │   │       └── a_rule_script.groovy
            │   ├── javascript
            │   │   ├── community
            │   │   │   └── something_from_the_community
            │   │   │       └── some_community_script.js
            │   │   ├── core
            │   │   │   ├── components
            │   │   │   └── 000_startup_delay.js
            │   │   └── personal
            │   │       └── a_rule_script.js
            │   └── python
            │       ├── community
            │       │   └── something_from_the_community
            │       │       └── some_community_script.py
            │       ├── core
            │       │   ├── components
            │       │   └── 000_startup_delay.py
            │       └── personal
            │           └── a_rule_script.py
            ├── jython
            │   └── jython-standalone-2.7.0.jar
            └── lib
                ├── groovy
                │   ├── community
                │   ├── core
                │   ├── personal
                │   └── configuration.groovy
                ├── groovy
                │   ├── community
                │   ├── core
                │   ├── personal
                │   └── configuration.js
                └── python
                    ├── community
                    ├── core
                    ├── personal
                    └── configuration.py

openHAB requires **scripts** to be located in the ``/automation/jsr223/`` subdirectory of the configuration directory:

    * package repository openHAB installation, like openHABian: ``/etc/openhab2/automation/jsr223/``
    * default Linux manual openHAB installation: ``/opt/openhab2/conf/automation/jsr223/``
    * default Windows manual openHAB installation: ``C:\openhab2\conf\automation\jsr223\``

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH components (trigger types, Item providers, etc.) are one example.
To prioritze the loading of scripts, a numeric prefix can be added to the name of the script. 
There are more details about the script load order in the `openHAB Scripted Automation documentation`_.

The **libraries** are located under the ``/automation/lib/`` directory. 

.. _openHAB Scripted Automation documentation: https://www.openhab.org/docs/configuration/jsr223.html
