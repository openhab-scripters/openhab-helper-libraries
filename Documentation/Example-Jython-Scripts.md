[[Home]](README.md)

## Example Jython Scripts

These scripts show example usage of various scripting features. 
Some of the examples are intended to provide services to user scripts, so they have a numeric prefix to force them to load first (but after the general purpose components). 
When using the instructions in the [Quick Start Guide](Getting-Started.md#quick-start-guide), these scripts should be copied to `/automation/jsr223/personal/`, as needed, in order to run them.
These scripts will import certain modules in the `core` package, so they will also need to be installed.

#### Script: [`hello_world.py`](/Script%20Examples/hello_world.py)
<ul>

This script has several examples for how to define Jython rules, just uncomment the ones you'd like to test. By default, it uses a decorated cron rule that will generate logs every 10s. This can be used to test your initial setup.
</ul>

#### Script: [`timer_example.py`](/Script%20Examples/timer_example.py)
<ul>

Example of a rule that shows how to create and cancel a global timer.
</ul>

#### Script: [`channel_event_example.py`](/Script%20Examples/channel_event_example.py)
<ul>

This script has several examples for rules triggered by Channel events.
</ul>

#### Script: [`action_example.py`](/Script%20Examples/action_example.py)
<ul>

Shows an example of using the `core.actions` module to access an Action.
</ul>

#### Script: [`rule_registry.py`](/Script%20Examples/rule_registry.py)
<ul>

This example shows how to retrieve the RuleRegistry service and use it to query rule instances based on tags,
enable and disable rule instances dynamically, and manually fire rules with specified inputs.
</ul>

#### Script: [`testing_example.py`](/Script%20Examples/testing_example.py)
<ul>

Examples of unit testing.
</ul>

#### Script: [`dirwatcher_example.py`](/Script%20Examples/dirwatcher_example.py)
<ul>

Example of a rule that watches for files created in a specified directory.
</ul>

#### Script: [`300_EchoThing.py`](/Script%20Examples/300_EchoThing.py)
<ul>

Experimental Thing binding and handler implemented in Jython. (At the time of this writing, 
it requires a small change to the ESH source code for it to work.) 
This simple Thing will write state updates on its input channel to items states linked to the output channel.
</ul>

#### Script: [`300_ExampleExtensionsProvider.py`](/Script%20Examples/300_ExampleExtensionsProvider.py)
<ul>

This component implements the openHAB extension provider interfaces, and can be used to provide symbols to a script namespace.
</ul>

#### Script: [`300_JythonConsoleCommand.py`](/Script%20Examples/300_JythonConsoleCommand.py)
<ul>

This script defines an command extension to the OSGI console. 
The example command prints some Jython platform details to the console output.
</ul>

#### Script: [`300_LogAction.py`](/Script%20Examples/300_LogAction.py)
<ul>

This is a simple rule action that will log a message to the openHAB log file.
</ul>

#### Script: [`actors.py`](/Script%20Examples/actors.py)
<ul>

Shows an example of using the Pykka actors library. The Pykka library must be in the Java classpath.
</ul>