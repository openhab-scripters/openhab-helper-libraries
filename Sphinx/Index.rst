******************************************************
Welcome to the openHAB Scripters Jython documentation!
******************************************************

This is a repository of experimental Jython code that can be used with the
`Eclipse SmartHome <https://www.eclipse.org/smarthome/>`_ platform and
`openHAB 2.x <http://openhab.org/>`_ (post OH snapshot build 1318).
A previous version with reduced functionality, but compatible with OH 2.3, has
been archived in this
`branch <https://github.com/OH-Jython-Scripters/openhab2-jython/tree/original_(%3C%3D2.3)>`_.

These works are based on the original contributions of Steve Bate, for which we
are very thankful!

.. note::
    The following documentation assumes that you have chosen to use Jython for
    JSR223 scripting in openHAB because you have at least a basic understanding
    of Python. If you have come here with no knowledge of Python, we recommend
    seeking out some tutorials to get you started with the language, such as
    `learnpython.org <https://www.learnpython.org/>`_.



.. toctree::
    :caption: Getting Started
    :maxdepth: 2

    Getting Started/Installation
    Getting Started/First Steps


.. toctree::
    :caption: How To's
    :maxdepth: 2

    How Tos/Rules.rst
    How Tos/Logging.rst


.. toctree::
    :caption: Design Patterns
    :maxdepth: 2


.. toctree::
    :caption: Core Modules
    :maxdepth: 2
    :glob:

    Core Modules/Rules.rst
    Core Modules/Triggers.rst
    Core Modules/Log.rst
    Core Modules/Actions.rst
    Core Modules/*


.. toctree::
    :caption: Community Modules
    :maxdepth: 2
    :glob:

    Community Modules/*


.. toctree::
    :caption: Contributing
    :maxdepth: 2

    Contributing/Writing Docs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
