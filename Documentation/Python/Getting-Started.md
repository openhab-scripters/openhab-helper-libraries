[[Jython Home]](README.md)

Directions specifically for installation in a Docker container are available [here](Docker.md).

### Additional Setup for Jython
<ul>

In addition to the steps documented in the [Quick Start Guide](/Docs/README.md#quick-start-guide), Jython will require the following:

1) Add/modify the EXTRA_JAVA_OPTS. 
These examples assume that you will be using the standalone Jython 2.7.0 jar (see step 2). 
Changes to the EXTRA_JAVA_OPTS require an OH restart. 

    **Using an `/etc/default/openhab2` file with a package repository OH installation (includes openHABian):**

    If creating a new file, remember to set the permissions so that the `openhab` account has at least read access.
    ```
    EXTRA_JAVA_OPTS="-Xbootclasspath/a:/etc/openhab2/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/etc/openhab2/automation/jython -Dpython.path=/etc/openhab2/automation/lib/python"
    ```
    **Using the `start.sh` script with a manual OH installation on Linux:**
    ```
    # Add to the top of the file
    export EXTRA_JAVA_OPTS="-Xbootclasspath/a:/opt/openhab2/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/opt/openhab2/conf/automation/jython -Dpython.path=/opt/openhab2/conf/automation/lib/python"
    ```
    **Using the `start.bat` script with a manual OH installation on Windows:**

    If you are not using OH 2.5, 2.5M2, S1604, or newer, you will first need to update your `C:\openhab2\runtime\bin\setenv.bat` with the [changes in the current file](https://github.com/openhab/openhab-distro/blob/master/distributions/openhab/src/main/resources/bin/setenv.bat#L121).
    ```
    REM Add to the top of the file
    set EXTRA_JAVA_OPTS=-Xbootclasspath/a:C:\openhab2\conf\automation\jython\jython-standalone-2.7.0.jar -Dpython.home=C:\openhab2\conf\automation\jython -Dpython.path=C:\openhab2\conf\automation\lib\python
    ```

2) Download the [standalone Jython 2.7.0 jar](http://www.jython.org/downloads.html) and copy it to the path specified above in the EXTRA_JAVA_OPTS. 
A full installation of Jython can also be used, but the paths above would need to be modified.
Jython 2.7.1 and 2.7.2a1+ will also work, but 2.7.0 has proven to be very stable.
3) After completing the steps in the [Quick Start Guide](/Docs/README.md#quick-start-guide), create rules using [rule and trigger decorators](Defining-Rules.md#rule-and-trigger-decorators). 
There is documentation on how to create rules directly with the API, but the decorators are by far the simplest.
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
See [Modifying Modules](Jython-Modules.md#modifying-modules).
</ul>
