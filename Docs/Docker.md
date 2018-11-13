[[Home]](README.md)

## Running Jython in an openHAB Docker image

This guide is written for openHAB v2.4, at the time of writing, it was Build #1390. To get this build, run `docker pull openhab/openhab:2.4.0-snapshot-amd64-debian`

Once you have openHAB installed and running, *with at least one item*, you can install Jython as follows (these are the steps I figured out after some trial and error).

### Installation

Install the "Rule Engine (Experimental)" add on. (In Paper UI, go to Add-ons > Misc, find the Rule Engine (Experimental), and click "INSTALL".

Once installed, Jython and supporting libraries can be installed into Openhab.

Get the files for openhab2-jython:
```
wget https://github.com/OH-Jython-Scripters/openhab2-jython/archive/master.zip
unzip master.zip
mv openhab2-jython-master/automation conf/
```
Note the last `mv` is to move the automation directory into the conf directory that's mounted in openHAB at `/openhab/conf/`. If you already have an `automation` directory, manually move over the individual directories.

Next, get and install the actual Jython binary:
```
curl http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar -o jython-standalone-2.7.0.jar
mkdir conf/automation/jython
mv jython-standalone-2.7.0.jar conf/automation/jython/
```
Again, the `conf` directory above is the directory that's mounted in openHAB.

Finally, copy over the `hello_world.py` script so we can see things happening in the logs.
```
cp openhab2-jython-master/Script\ Examples/hello_world.py conf/automation/jsr223/
```

### Docker Environment

Then, when starting the docker container, include the environment variable as follows:
```
-e "EXTRA_JAVA_OPTS=-Xbootclasspath/a:/openhab/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/openhab/conf/automation/jython -Dpython.path=/openhab/conf/automation/lib/python"
```
Or, if you are using a compose file, include this:
```
    environment:
      EXTRA_JAVA_OPTS: "-Xbootclasspath/a:/openhab/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/openhab/conf/automation/jython -Dpython.path=/openhab/conf/automation/lib/python"
```

Then restart openHAB. You should see something such as this in the logs:
```
2018-10-17 02:18:06.704 [INFO ] [.internal.GenericScriptEngineFactory] - Activated scripting support for python
```

Then, after a minute or two, this should appear in the logs every 10 seconds or so:
```
2018-10-17 02:24:40.077 [INFO ] [eclipse.smarthome.model.script.Rules] - JSR223: This is a 'hello world!' from a Jython rule (decorator): Cron
```
