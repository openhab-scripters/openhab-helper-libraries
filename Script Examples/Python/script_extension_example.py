"""
This is an example script to illustrate the creation/modification of
ScriptExtension presets. Save the script file twice.
"""
scriptExtension.importPreset(None)# fix for compatibility with Jython > 2.7.0
from core.log import logging, LOG_PREFIX
LOG = logging.getLogger("{}.TEST".format(LOG_PREFIX))

if "variable_3" in locals():
    """
    ``variable_3`` will not be available until after the first run of the
    script, which creates ``test_default_preset``.
    """
    LOG.warn("This is the default script scope plus the things from the custom test_default_preset (variable_1 and variable_2): dir() \n{}".format(dir()))
    LOG.warn("variable_3 [{}]".format(variable_3))# pylint: disable=undefined-variable
    LOG.warn("variable_4 [{}]".format(variable_4))# pylint: disable=undefined-variable
else:
    import core
    LOG.warn("These are the stock presets: scriptExtension.presets \n{}".format(scriptExtension.presets))
    LOG.warn("These are the stock default presets loaded into every script scope: scriptExtension.defaulPresets \n{}".format(scriptExtension.defaultPresets))
    LOG.warn("This is the default script scope plus core, core.log.logging, core.log.LOG_PREFIX, and LOG: dir() \n{}".format(dir()))

    core.JythonExtensionProvider.addValue("variable_1", 1)
    core.JythonExtensionProvider.addValue("variable_2", 2)
    core.JythonExtensionProvider.addPreset("test_non-default_preset", ["variable_1", "variable_2"], False)
    LOG.warn("These are the stock presets plus test_non-default_preset: scriptExtension.presets \n{}".format(scriptExtension.presets))
    LOG.warn("You can just get the values directly without importing, but this will confuse people: scriptExtension.get(\"variable_1\") [{}]".format(scriptExtension.get("variable_1")))# pylint: disable=undefined-variable
    scriptExtension.importPreset("test_non-default_preset")
    LOG.warn("This is the same script scope as before, plus the things from test_non-default_preset (variable_1 and variable_2), after it was imported: dir() \n{}".format(dir()))
    LOG.warn("variable_1 [{}]".format(variable_1))# pylint: disable=undefined-variable
    LOG.warn("variable_2 [{}]".format(variable_2))# pylint: disable=undefined-variable

    core.JythonExtensionProvider.addValue("variable_3", 3)
    core.JythonExtensionProvider.addValue("variable_4", 4)
    core.JythonExtensionProvider.addPreset("test_default_preset", ["variable_3", "variable_4"], True)
    LOG.warn("These are the stock presets plus non-test_default_preset and test_default_preset: scriptExtension.presets \n{}".format(scriptExtension.presets))
    LOG.warn("These are the stock default presets, plus test_default_preset: scriptExtension.defaulPresets \n{}".format(scriptExtension.defaultPresets))
