# Helper Libraries for openHAB Scripted Automation

>***
>## <p style="text-align: center;">***** **UNDER CONSTRUCTION** *****</p>
>The openHAB Scripters (formerly OH Jython Scripters) organization and this repository have both recently had name changes, and there has been a directory restructuring to support more languages. 
Javascript libraries are now included, but they require testing and are likely to have frequent updates as the functionality of the Jython libraries are added to them. 
Please report any issues that you find! 
>
>If you have local repositories, you'll need to [update them to point to the new location](https://help.github.com/en/articles/changing-a-remotes-url).
>***

These libraries can be used with [openHAB](http://openhab.org/) (2.4M3, S1319, or newer) and the new rule engine. 
The one exception is that custom module handlers, including the StartupTrigger, DirectoryTrigger, and OsgiEventTrigger in the JythonHLs, require S1566 or newer.

### Quick Start Guide

1) The [Next-Generation Rule Engine](https://www.openhab.org/docs/configuration/rules-ng.html) is still in development, so it is recommended to use the latest snapshot or milestone release of openHAB. 
2) Use the [Karaf logging]({{base}}/administration/logging.html) commands to enable debug logging for automation: 

    `log:set DEBUG org.openhab.core.automation`

    Leave this on for setup and testing, but you may want to set to WARN when everything is setup. 
For older openHAB builds before the ESH reintegration (older than snapshot 1566 and 2.5M2), you will need to changed this to `org.eclipse.smarthome.automation`. 
3) Enable debug logging for jsr223: 

    `log:set DEBUG jsr223`

    This is the default logger used in the examples and the helper libraries.
4) Review the general [openHAB JSR223 Scripting](https://www.openhab.org/docs/configuration/jsr223.html) and the language specific documentation found as links on that page. 
5) Install the [Next-Generation Rule Engine](https://www.openhab.org/docs/configuration/rules-ng.html) add-on.
6) Shut down openHAB.
7) [Download the contents of this repository](https://github.com/openhab-scripters/openhab-helper-libraries/archive/master.zip) and, using the openHAB account, copy the _contents_ of the `/Core/` directory into: 
    - `/etc/openhab2/` (package repository OH install, like openHABian)
    - `/opt/openhab2/conf/` (default manual OH install).
 
    This will create a directory structure, as described in [File Locations](#File-Locations). 
This will contain all of the Core files for each language, including the startup delay scripts that ensure OH has started completely before loading other scripts.
If you do not plan to use all of the languages, you may want to remove the directories for them under `/automation/jsr223/` and `/automation/lib/`.
8) There is a main configuration file for each scripting language's helper libraries that will need to be renamed. 
For example, in `\automation\lib\python\`, rename the file `configuration.py.example` to `configuration.py`. 
These files can be used to secure personal information, so that they are not stored in files that may be shared with the community, or to store variables that are accesed by multiple scripts and/or modules, e.g. LOG_PREFIX. 
9) For Jython, follow the steps in the [Getting Started](Python/Getting-Started.md#additional-setup-for-jython). For Groovy, follow the steps in the [Getting Started](Groovy/README.md#additional-setup-for-groovy). When complete, come back here. 
10) Copy the Hello World example script for the language(s) that you are using to the `jsr223` directory:
    - copy [`/Script Examples/Python/hello_world.py`](/Script%20Examples/Python/hello_world.py) to `/automation/jsr223/python/personal/`
    - copy ['/Script Examples/Javascript/HelloWorld.js'](/Script%20Examples/Javascript/HelloWorld.js) to `/automation/jsr223/javascript/personal/`)
    - copy ['/Script Examples/Groovy/HelloWorld.groovy'](/Script%20Examples/Groovy/HelloWorld.groovy) to `/automation/jsr223/groovy/personal/`) 
11) Start openHAB and watch the logs for errors and the entries from the Hello World script.
This script will make a log entry every 10s, and should be deleted after installation has been verified.
12) Review the language specific helper library documentation: 
    - [Groovy](Groovy/README.md)
    - [Javascript](Javascript/README.md)
    - [Jython (Python)](Python/README.md)
13) Ask questions on the [openHAB forum](https://community.openhab.org/tags/jsr223) and tag posts with `jsr223`. Report issues [here](https://github.com/openhab-scripters/openhab-helper-libraries/issues), but please don't hesitate to update the documentation and code. 
Just like openHAB, this repository is community driven!

### File Locations
<ul>

Example Directory Structure:

```text
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
```

openHAB requires **scripts** to be located in the `/automation/jsr223/` subdirectory of the configuration directory. 
- Linux package repository installation, like openHABian: `/etc/openhab2/automation/jsr223/`
- Linux manual installation: `/opt/openhab2/conf/automation/jsr223/`
- Windows manual installation: `C:\openhab2\conf\automation\jsr223\`

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH components (trigger types, Item providers, etc.) are one example.
To prioritze the loading of scripts, a numeric prefix can be added to the name of the script. 
There are more details about the script load order in the [openHAB JSR223 documentation](https://www.openhab.org/docs/configuration/jsr223.html#script-locations).

The **libraries** are located under the `/automation/lib/` directory. 
</ul>
