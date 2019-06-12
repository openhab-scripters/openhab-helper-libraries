************************************************
Helper Libraries for openHAB Scripted Automation
************************************************

.. admonition:: **UNDER CONSTRUCTION**

    The openHAB Scripters (formerly OH Jython Scripters) organization and this repository have both recently had name changes, and there has been a directory restructuring to support more languages.
    Javascript libraries are now included, but they require testing and are likely to have frequent updates as the functionality of the Jython libraries are added to them.
    Please report any issues that you find!

    If you have local repositories, you'll need to update them to point to the `new location`_.

The main purpose of the helper libraries is to provide a layer of abstraction to simplify the interaction of scripts with the openHAB Automation API.
These libraries can be used with `openHAB`_ (2.4M3, S1319, or newer) and the `Next-Generation Rule Engine`_.
The one exception is that custom module handlers, including the StartupTrigger, DirectoryTrigger, and OsgiEventTrigger in the JythonHLs, require S1566 or newer.

.. toctree::
    :caption: Getting Started
    :includehidden:
    :maxdepth: 2

    Getting Started/Installation/Installation.rst
    Getting Started/File Locations.rst
    Getting Started/First Steps.rst


.. toctree::
    :caption: Guides
    :maxdepth: 2

    Guides/Rules.rst
    Guides/Triggers.rst
    Guides/Logging.rst
    Guides/Event Object Attributes.rst
    Guides/But How Do I.rst


.. toctree::
    :caption: Packages
    :maxdepth: 2

    Core/Core.rst
    Community/Community.rst


.. toctree::
    :caption: Design Patterns
    :maxdepth: 2


.. toctree::
    :caption: Language Specific
    :maxdepth: 2
    :glob:

    Language Specific/Python.rst
    Language Specific/*


.. toctree::
    :caption: Contributing
    :maxdepth: 2

    Contributing/Coding Guidelines
    Contributing/Writing Docs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _openHAB: https://www.openhab.org
.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
.. _new location: https://help.github.com/en/articles/changing-a-remotes-url
