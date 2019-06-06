[[Jython Home]](README.md)

## Component Scripts

When using the instructions in the [Quick Start Guide](Getting-Started.md#quick-start-guide), these modules should be located in `/automation/jsr223/core/components/`. 
The files have a numeric prefix to cause them to be loaded before regular user scripts.

#### Script: [`100_DirectoryTrigger.py`](../../Core/automation/jsr223/python/core/components/100_DirectoryTrigger.py)
<ul>

This trigger can respond to file system changes.
For example, you could watch a directory for new files and then process them.

```python
@rule("Directory watcher example")
class DirectoryWatcherExampleRule(object):
    def getEventTriggers(self):
        return [ DirectoryEventTrigger("/tmp", event_kinds=[ENTRY_CREATE]).trigger ]
    
    def execute(self, module, inputs):
        logging.info("detected new file: %s", inputs['path'])
```
</ul>

#### Script: [`100_OsgiEventTrigger.py`](../../Core/automation/jsr223/python/core/components/100_OsgiEventTrigger.py)
<ul>

This rule trigger responds to events on the OSGI EventAdmin event bus.
</ul>

#### Script: [`100_StartupTrigger.py`](../../Core/automation/jsr223/python/core/components/100_StartupTrigger.py)
<ul>

Defines a rule trigger that triggers immediately when a rule is activated. [not functional yet]
</ul>

#### Script: [`200_JythonExtensionProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonExtensionProvider.py)
<ul>

This component implements the openHAB extension provider interfaces, and can be used to provide symbols to a script
namespace.
</ul>

#### Script [`200_JythonTransform.py`](../../Core/automation/jsr223/python/core/components/200_JythonTransform.py)
<ul>

This script defines a transformation service (identified by "JYTHON") that will process a value using a Jython script. 
This is similar to the Javascript transformation service.
</ul>

#### Script [`200_JythonItemProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonItemProvider.py)
<ul>

This script adds an ItemProvider, so that Items can be added and removed at runtime.
</ul>

#### Script [`200_JythonItemChannelLinkProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonItemChannelLinkProvider.py)
<ul>

This script adds an ItemChannelLinkProvider, so that Links can be added and removed at runtime.
</ul>

#### Script [`200_JythonBindingInfoProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonBindingInfoProvider.py)
<ul>

This script adds a BindingInfoProvider.
</ul>

#### Scripts: Jython-based Thing Providers
<ul>

These components are used to support Thing Handler implementations:
* [`200_JythonThingProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonThingProvider.py)
* [`200_JythonThingTypeProvider.py`](../../Core/automation/jsr223/python/core/components/200_JythonThingTypeProvider.py)
</ul>