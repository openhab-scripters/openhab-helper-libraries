[[Home]](README.md)

### Quick Start Guide

Directions specifically for installation in a Docker container are available [here](Docker.md).

- Since the ESH automation API is still under development, it is best to use a current testing or snapshot release of openHAB. 
More importantly, there are breaking changes in the API, so at least OH 2.4 snapshot 1319 or milestone M3 is required to use these modules.
- Install the [Experimental Rule Engine](https://www.openhab.org/docs/configuration/rules-ng.html) add-on.
- Review the [JSR223 Jython documentation](https://www.openhab.org/docs/configuration/jsr223-jython.html).
- Turn on debugging for org.eclipse.smarthome.automation (`log:set DEBUG org.eclipse.smarthome.automation` in Karaf). Leave this on for setup and testing, but you may want to set to WARN when everything is setup.
- Shut down openHAB.
- Download the contents of this repository and, using the openHAB account, copy the _contents_ of the `/Core/` directory into `/etc/openhab2/` (package repository OH install, like openHABian) or `/opt/openhab2/conf/` (default manual OH install). 
This will create a directory structure as described in [File Locations](#file-locations), and will include all of the Core files, including a startup delay script that insures OH is started completely before loading other scripts.
- Add/modify your EXTRA_JAVA_OPTS. 
These examples assume that you will be using the standalone Jython 2.7.0 jar. 

    **Using an `/etc/default/openhab2` file with a package repository OH installation (includes openHABian):**
    If creating a new file, remember to set the permissions so that the OH account has read access.
    ```
    EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"
    ```
    **Using the `start.sh` script with a manual OH installation:**
    ```
    export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"
    ```
- Download the [standalone Jython 2.7.0 jar](http://www.jython.org/downloads.html) and copy it to the path specified above. 
A full install of Jython can also be used, but the paths above will need to be modified. 
- Copy the [`hello_world.py`](/Script%20Examples/hello_world.py) example script to `/automation/jsr223/personal/` to test if everything is working. 
This script will make a log entry every 10s, and should be deleted after installation has been verified.
- Start openHAB and watch the logs for errors and the entries from the `hello_world.py` script.
- Review the general [openHAB JSR223 scripting documentation](https://www.openhab.org/docs/configuration/jsr223.html).
- Review the rest of this documentation.
- Create rules using [rule and trigger decorators](Defining-Rules.md#rule-and-trigger-decorators). 
There is documentation on how to create rules directly with the ESH API, but the decorators are by far the simplest.
- Ask questions on the [openHAB forum](https://community.openhab.org/tags/jsr223) and tag posts with `jsr223`. Report issues [here](https://github.com/OH-Jython-Scripters/openhab2-jython/issues), but please don't hesitate to update the documentation and code. 
Just like OH, this repository is community driven!

### Applications
<ul>

The [JSR223 scripting extensions](https://www.jcp.org/en/jsr/detail?id=223) can be used for general scripting purposes, 
including defining rules and associated SmartHome rule "modules" (triggers, conditions, actions). 
Some possible applications include integration testing of complex rule behaviors or prototyping new OH2/ESH functionality.

(_JSR223_ refers to a Java specification request for adding scripting to the Java platform. 
That term will not be used in Java versions 9 and above. 
The previous JSR223 functionality will be provided by the Java `javax.script` package in the standard runtime libraries.)

The scripting can be used for other purposes like automated integration testing 
or to access the OSGI framework (using or creating services, for example).
</ul>

### Jython Scripts and Modules
<ul>

It's important to understand the distinction between Jython _scripts_ and Jython _modules_. 

A Jython script is loaded by the `javax.script` script engine manager (JSR223) integrated into ESH (openHAB 2). 
Each time the file is loaded, OH2 creates a execution context for that script.
When the file is modified, OH2 will destroy the old script context and create a new one.
This means any variables defined in the script will be lost when the script is reloaded.

A Jython module is loaded by Jython itself through the standard Python `import` directive and uses `sys.path`.
The normal Python module loading behavior applies.
This means the module is normally loaded only once, and is not reloaded when the module source code changes.
</ul>

### File Locations
<ul>

Example Directory Structure:

```text
|_ etc
    |_ openhab2
        |_ automation
            |_ jsr223
                |_ community
                    |_ something_from_the_community
                        |_ some_community_script.py
                |_ core
                    |_ components
                    |_ 000_startup_delay.py
                |_ personal
                    |_ my_rule_script.py
            |_ lib
                |_ python
                    |_ community
                    |_ openhab
                    |_ personal
                    |_ configuration.py
```
ESH requires scripts to be located in the `/automation/jsr223/` subdirectory hierarchy of your OH2 configuration directory. 
In a Linux package repository installation, like openHABian, this would be `/etc/openhab2/automation/jsr223/`. 
For a Linux manual installation, this would default to `/opt/openhab2/conf/automation/jsr223/`. 

The modules are located in the `/automation/lib/python/` directories. 
They can be moved anywhere, but the Python path must be configured to find them.
There are several ways to do this. 
You can add a `-Dpython.path=mypath1:mypath2` to the JVM command line by modifying the OH2 startup scripts.
You can also modify the `sys.path` list in a Jython script that loads early (like a component script).
Another option is to checkout the GitHub repo in some location and use a directory soft link (Linux) 
from `/etc/openhab2/automation/lib/python/core` to the GitHub workspace directory `/Core/automation/jsr223/lib/python/core`.

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH2 components (like trigger types, item providers, etc.) are one example.
To prioritze the loading of scripts, a numeric prefix can be added to the name of the script. 
</ul>
