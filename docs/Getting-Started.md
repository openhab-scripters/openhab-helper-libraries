[[Home]](README.md)

### Quick Start Guide

- Since JSR223 is still under development, it is best to use a current testing or snapshot release of openHAB. 
More importantly, there are breaking changes in the API, so at least OH snapshot 1319 or milestone M3 are required to use these modules.
- Install the [Experimental Rule Engine](https://www.openhab.org/docs/configuration/rules-ng.html) add-on.
- Review the [JSR223 Jython documentation](https://www.openhab.org/docs/configuration/jsr223-jython.html).
- Turn on debugging for org.eclipse.smarthome.automation (`log:set DEBUG org.eclipse.smarthome.automation` in Karaf). Leave this on for setup and testing, but you may want to set to WARN when everything is setup.
- Download the contents of this repository and copy the `automation` directory into `/etc/openhab2/` (package repository OH install, like openHABian) or `/opt/openhab2/conf` (default manual OH install).
- Add/modify your EXTRA_JAVA_OPTS. These examples assume that you will be using the standalone Jython 2.7.0 jar. 

    **Using a `/etc/default/openhab2` file with a package repository OH installation (includes openHABian):**
    ```
    EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"
    ```
    **Using the `start.sh` script with a manual OH installation:**
    ```
    export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"
    ```
- Download the [standalone Jython 2.7.0 jar](http://www.jython.org/downloads.html) and copy it to the path specified above. A full install of Jython can also be used, but the paths above will need to be modified.
- Restart OH and watch the logs for errors.
- Copy the [`hello_world.py`](/Script%20Examples/hello_world.py) example script to `/automation/jsr223/` to test if everything is working. This script will make a log entry every 10s.
- Review the general [openHAB2 JSR223 scripting documentation](http://docs.openhab.org/configuration/jsr223.html).
- Review the rest of this documentation.
- Create rules using [rule and trigger decorators](#rule-and-trigger-decorators).
- Ask questions on the [openHAB forum](https://community.openhab.org/tags/jsr223) and tag posts with `jsr223`. Report issues [here](https://github.com/OH-Jython-Scripters/openhab2-jython/issues).

Some directions specifically for Docker are available at [Docker.md](Docker.md)

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
In this repo, scripts are in the `scripts` directory and modules are in the `lib` directory.

A Jython script is loaded by the `javax.script` script engine manager (JSR223) integrated into openHAB 2. 
Each time the file is loaded, OH2 creates a execution context for that script.
When the file is modified, OH2 will destroy the old script context and create a new one.
This means any variables defined in the script will be lost when the script is reloaded.

A Jython module is loaded by Jython itself through the standard Python `import` directive and uses `sys.path`.
The normal Python module loading behavior applies.
This means the module is loaded once and is not reloaded when the module source code changes.
</ul>

### File Locations
<ul>

Scripts should be put into the `/automation/jsr223/` subdirectory hierarchy of your OH2 configuration directory.
In a Linux package repository installation, like openHABian, this would be `/etc/openhab2/automation/jsr223/`. For a Linux manual installation, this would default to `/opt/openhab2/conf/automation/jsr223/`.

Some scripts should be loaded before others because of dependencies between the scripts. 
Scripts that implement OH2 components (like trigger types, item providers, etc.) are one example.
It is recommended to put these scripts into a subdirectory called `000_Components`. 
The name prefix will cause the scripts in the directory to be loaded first.
It is also recommended to name the component files with a `000_` prefix, 
because there are currently bugs in the file loading behavior of OH2 (ref? likely resolved).

Example:

```text
|_ etc
    |_ openhab2
        |_ automation
            |_ jsr223
                |_ 000_Components
                    |_ 000_StartupTrigger.py
                |_ my_rule_script.py
```

Jython modules can be placed anywhere, but the Python path must be configured to find them.
There are several ways to do this. 
You can add a `-Dpython.path=mypath1:mypath2` to the JVM command line by modifying the OH2 startup scripts.
You can also modify the `sys.path` list in a Jython script that loads early (like a component script).

Another option is to checkout the GitHub repo in some location and use a directory soft link (Linux) 
from `/etc/openhab2/automation/lib/python/openhab` to the GitHub workspace `automation/lib/python/openhab` directory.
</ul>