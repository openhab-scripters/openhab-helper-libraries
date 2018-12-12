import collections

import core
from core.log import logging, LOG_PREFIX
log = logging.getLogger(LOG_PREFIX + ".JythonExtensionProvider")

def scriptLoaded(*args):    
    try:
        from java.lang import Class
        name = "org.eclipse.smarthome.automation.module.script.ScriptExtensionProvider"
        ScriptExtensionProvider = Class.forName(name, True, scriptExtension.getClass().getClassLoader())
        
        class JythonExtensionProvider (ScriptExtensionProvider):            
            def __init__(self):
                self._defaultPresets = set()
                self._presets = set()
                self._preset_values = collections.defaultdict(list)
                self._values = {}
                
            def getDefaultPresets(self):
                """These presets will always get injected into the ScriptEngine on instance creation."""
                return self._defaultPresets

            def getPresets(self):
                """Returns the provided Presets which are supported by this ScriptExtensionProvider.
                    Presets define imports which will be injected into the ScriptEngine if called by "importPreset".
                    Note: default preset names must also be in this list.
                """
                return self._presets

            def getTypes(self):
                """Returns the supported types which can be received by the given ScriptExtensionProvider.
                    "Types" are just names and can refer to any object, either instance or class."""
                return self._values.keys()
           
            def get(self, scriptIdentifier, name):
                """This method should return an Object of the given type. Note: get can be called 
                    multiple times in the scripts use caching where appropriate. The scriptIdentifier can
                    be used to create script-specific values."""
                return self._values.get(name) 
        
            def importPreset(self, scriptIdentifier, preset):
                """This method should return variables and types of the concrete type which
                    will be injected into the ScriptEngines scope."""
                # scriptIdentifier is ignored
                return {name: self._values.get(name) for name in self._preset_values.get(preset, [])}
        
            def unload(self, scriptIdentifier):
                """This will be called when the ScriptEngine will be unloaded (e.g. if the Script is deleted or updated).
                    Script-specific information should be removed."""
                # scriptIdentifier is ignored
                pass
            
            def addValue(self, name, value):
                self._values[name] = value
                
            def addValues(self, values):
                self._values.update(values)
                
            def addPreset(self, preset_name, value_names, is_default=False):
                self._presets.add(preset_name)
                self._preset_values[preset_name] = value_names
                if is_default:
                    self._defaultPresets.add(preset_name)
 
        core.JythonExtensionProvider = JythonExtensionProvider()
        scriptExtension.addScriptExtensionProvider(core.JythonExtensionProvider)
    except:
        core.JythonExtensionProvider = None
        import traceback
        log.error(traceback.format_exc())

def scriptUnloaded():
    if core.JythonExtensionProvider is not None:
        scriptExtension.removeScriptExtensionProvider(core.JythonExtensionProvider)
        core.JythonExtensionProvider = None
            
