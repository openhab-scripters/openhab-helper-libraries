"""
Example of using the openHAB extension provider interfaces and can be used to provide symbols to a script namespace.
"""

from core import JythonExtensionProvider

JythonExtensionProvider.addValue("Foo", 1)
JythonExtensionProvider.addValue("Bar", "x")
JythonExtensionProvider.addValue("Baz", {"a": 10})
JythonExtensionProvider.addPreset("P1", ["Foo"], True)
JythonExtensionProvider.addPreset("P2", ["Bar", "Baz"])
