[[Home]](README.md)

## Example-Jython-Scripts

These scripts show example usage of various scripting features. 
Some of the examples are intended to provide services to user scripts so they have a numeric prefix to force them to load first 
(but after the general purpose components). In order to use them, these scripts can be copied to a subdirectory of `/automation/jsr223/` to test them.
These scripts will import certain modules, so they will also need to be instaled.

These scripts must be copied to a subdirectory of `/automation/jsr223/`.

#### Script: [`hello_world.py`](../Script Examples/hello_world.py)
<ul>

This script has several examples for how to define Jython rules, just uncomment the ones you'd like to test. By default, it uses a decorator cron rule that will generate logs every 10s. This can be used to test your initial setup.
</ul>

#### Script: [`000_LogAction.py`](../Script Examples/000_LogAction.py)
<ul>

This is a simple rule action that will log a message to the openHAB log file.
</ul>

#### Script: [`100_EchoThing.py`](../Script Examples/100_EchoThing.py)
<ul>

Experimental Thing binding and handler implemented in Jython. (At the time of this writing, 
it requires a small change to the ESH source code for it to work.) 
This simple Thing will write state updates on its input channel to items states linked to the output channel.
</ul>

#### Script: [`000_JythonConsoleCommand.py`](../Script Examples/000_JythonConsoleCommand.py)
<ul>

This script defines an command extension to the OSGI console. 
The example command prints some Jython platform details to the console output.
</ul>

#### Script: [`actors.py`](../Script Examples/actors.py)
<ul>

Shows an example of using the Pykka actors library. The Pykka library must be in the Java classpath.
</ul>

#### Script: [`esper_example.py`](../Script Examples/esper_example.py)
<ul>

Shows an example of using the Esper component. The 000_Esper.py component script must be installed.
</ul>

#### Script: [`rule_decorators.py`](../Script Examples/rule_decorators.py)
<ul>

Provides examples of using the trigger-related rule decorators on functions as an alternative to explicit rule and trigger classes.
</ul>

#### Script: [`testing_example.py`](../Script Examples/testing_example.py)
<ul>

Examples of unit testing.
</ul>

#### Script: [`dirwatcher_example.py`](../Script Examples/dirwatcher_example.py)
<ul>

Example of a rule that watches for files created in a specified directory.
</ul>

#### Script: [`rule_registry.py`](../Script Examples/rule_registry.py)
<ul>

This example shows how to retrieve the RuleRegistry service and use it to query rule instances based on tags,
enable and disable rule instances dynamically, and manually fire rules with specified inputs.
</ul>

#### Script: [`timer_example.py`](../Script Examples/timer_example.py)
<ul>

Example of a rule that shows how to create and cancel a global timer.
</ul>
