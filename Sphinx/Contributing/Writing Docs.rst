*********************
Writing Documentation
*********************

This document will show you how to format Python *docstrings* using
reStructuredText and what files you need to create so that Sphinx will pull the
*docstrings* from your module. There are also instructions on how to setup
Sphinx to build the docs so that you can verify that your documentation is
rendering correctly.


Python docstrings
=================

  Python *docstrings* are a type of documentation that is actually a part of
  the code itself. The Sphinx extension ``autodoc`` extracts these strings and
  uses them to build documentation webpages automatically. This section will go
  over where to put these *docstrings*, what format they need to follow, and
  what information they need to contain.

Format
------

    This documentation is using a Sphinx extension called ``napoleon`` that
    parses `Google <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_
    style *docstrings* and converts them to reStructuredText for use in these
    pages. All documentation here should follow that guide fairly closely.

    All *docstrings* should be contained within triple double-quotes ``"""``
    with the exception of inline *docstrings* for attributes or aliases which
    follow ``#:`` at the end of the line like a comment.

File Header
-----------

    Each module page should be reading the header *docstring* from the file.
    It must be the first thing in the file.

    * If your addition is only a single module, it should start with a
      *docstring* in the format below.

    * If your addition is a package with several files:

      * The main page should be reading its *docstring* from your package's
        ``__init__.py``. It should contain and overview of what your package
        does. If your module does not have an ``__init__.py`` file, you should
        put this information above the ``.. toctree::`` directive in the main
        ``.rst`` file for your package (more on directives later).
      * All modules or files with their own page should also read *docstrings*
        from those files. They should give an overview of what the module is
        intended for.

    This is an example of what a header *docstring* should look like:

    .. code-block::

      """
      One line summary of your module or package.

      Longer description of your module or package and its use
      should go here. It can be as long or short as you need.
      Inline reST markdowns can be used, as well as directives like
      '.. code-block::' if you need them.
      """

Module Attributes
-----------------

    Modules with public attributes should have *docstrings* for them. These can
    be inline using ``#:`` at the end of the line, or on the following line
    like functions and methods.

    .. code-block::

      my_public_attr = True   #: short description of attr

      my_other_attr = False
      """description of attr"""

Functions and Methods
---------------------

    All functions and methods should have *docstrings* unless they are private
    or their use is obvious. They should follow the `Functions and Methods <https://google.github.io/styleguide/pyguide.html#383-functions-and-methods>`_
    guidelines for content and format.

Classes
-------

    All classes should have *docstrings* unless they are private. They should
    follow the `Classes <https://google.github.io/styleguide/pyguide.html#384-classes>`_
    guidelines for content and format, except for the ``__init__`` method.
    The class *docstring* should also contain a description of the ``__init__``
    method and its arguments.


Adding Documentation for Modules
================================

  When you are contributing a new module or package to this repo you need to
  add a simple reST file (``.rst``) to allow Sphinx to extract the Python
  *docstrings* from your module. This file must have the same name as your
  module or package

  .. warning::
    | *autodoc* is used to read the *docstrings* from the code and is also
      written in python and will import your module. This means that any
      imports or code that runs when loaded will be executed.
    | In particular for this library, it means that *autodoc* will throw errors
      when trying to import openHAB classes, the solution to this is outlined
      in :ref:`Contributing/Writing Docs:Building the Docs`

Module Documentation
--------------------

    If your addition is only a single module, you will only need to create one
    file. This file must have the same name as your module to avoid naming
    conflicts with other modules, and be in the ``/Sphinx/Community/``
    directory.

    .. code-block:: bash

      /Community/my_module.py
      /Sphinx/Community/my_module.rst

    Below is an example of what is required in this file:

    .. code-block:: rest

      My Module
      =========

      .. automodule:: community.my_module

    * The heading is the name of your module as it should appear in the
      documentation, the ``===`` line below it must be at least the same length
      as the heading.
    * ``.. automodule:: community.my_module`` instructs Sphinx to parse
      ``/Community/my_module.py``.
    * All ``.rst`` files must end with a blank line

    You should now go to the :ref:`Contributing/Writing Docs:Building the Docs`
    section and make sure your documentation is compiling and rendering
    correctly.

    More advanced parsing options are documented `here <http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_
    if you need them.

Package Documentation
---------------------

    If your addition is a package it will require a minimum of one page, but
    it is also possible for each module to have its own page in the docs. If
    your package will only have one page, follow the instructions above for
    :ref:`Contributing/Writing Docs:Module Documentation`. If your package will
    have multiple pages, follow the instructions below.

    1.  | Create an ``.rst`` file for each module in your package that should
          have a page and place them
          in ``/Sphinx/Community/my_package/``, using the content for a
          single page module.
        | Use ``---`` instead of ``===`` under the heading.
    2.  Then create an ``.rst`` file in the ``/Sphinx/Community/``
        directory with the same name as your package, with the following content:

        .. code-block:: rest

          My Package
          ==========

          .. automodule: community.my_package

          .. toctree::
            :maxdepth: 1
            :glob:

            my_package/*

    * The heading is the name of your package as it should appear in the
      documentation, the ``===`` line below it must be at least the same length
      as the heading.
    * ``.. automodule: community.my_package`` will pull the *docstring* from
      your package's ``__init__.py`` to describe its purpose.
    * ``:maxdepth:`` should always be ``1``.
    * ``:glob:`` tells Sphinx to look for any ``.rst`` files in the directories
      listed below.
    * | ``my_package/*`` Sphinx will look for any ``.rst`` files in the
        directory and add them in alphabetical order.
      | Alternatively, if you want to control the order you can specify each
        documentation file manually, in the order you want them to appear. You
        may also specify some files and glob the rest, each file will only
        appear once.
    * All ``.rst`` files must end with a blank line

    You should now have created files similar to the following for your package.

    .. code-block:: bash

      /Community/my_package/__init__.py
      /Community/my_package/my_module.py
      /Sphinx/Community/my_package.rst
      /Sphinx/Community/my_package/my_module.rst

    You should now go to the :ref:`Contributing/Writing Docs:Building the Docs`
    section and make sure your documentation is compiling and rendering
    correctly.


Building the Docs
=================

  When writing documentation for a module or package we ask that you build the
  docs and make sure that your pages are appearing correctly. This will also
  allow you to view what the rendered docs will look like if you are using
  any formatting. If you do not build the documentation yourself and verify it,
  a maintainer will have to do it and this will delay merging your package.

  This section will go over all of the steps to build the docs from nothing.
  If you already have a Virtual Environment setup for this, you can skip to
  :ref:`Contributing/Writing Docs:Building`.

Virtual Environment
-------------------

    We recommend you use a virtual environment for building the docs, this way
    your local Python installation remains unchanged. This section will walk
    you through creating a virtual environment and setting it up to build the
    docs.

    First, make sure you have ``python3`` and ``python3-pip`` installed:

    .. code-block:: bash

      $ sudo apt install python3 python3-pip

    All of the following instructions must be run from the root of the
    repository on your computer.

    Next we create a virtual environment:

    .. code-block:: bash

      $ python3 -m venv .venv

    Now we will switch to that environment instead of your local python install:

    .. code-block:: bash

      $ source .venv/bin/activate

    After activating the environment your prompt should change to this:

    .. code-block:: bash

      (.venv) $

    Finally we will install Sphinx and the other modules used:

    .. code-block:: bash

      (.venv) $ pip3 install sphinx mock sphinx-tabs

Building
--------

    Once you have created the ``.rst`` files needed for your module to be
    documented you need to have Sphinx rebuild the html files.

    From the repo root, first make sure you are using your virtual environment:

    .. code-block:: bash

      $ source .venv/bin/activate

    Then run the Sphinx build script:

    .. code-block:: bash

      (.venv) $ Sphinx/build-docs.sh

    This should produce some output and end with ``build succeeded.``

    If the build produces any errors, they must be fixed before your pull
    request can be merged. If you are seeing any Import Errors, see the next
    section. If you are seeing other errors and are not able to resolve them,
    make your pull request and ask for help.

Import Errors
-------------

    In order to read the *docstrings* from your modules, ``autodoc`` needs to
    import it. This can lead to issues trying to import modules that the
    Sphinx environment doesn't have access to.

    In our particular case, this includes every Java import. Thankfully there
    are ways around this. The easiest way is adding the base package name to
    ``autodoc_mock_imports`` in ``/Sphinx/conf.py``. The most common ``org``
    and ``java`` packages are already there.

    If ``org`` is removed from that list, you will see errors like this:

    .. code-block:: bash

      WARNING: autodoc: failed to import module 'date' from module 'core'; the following exception was raised:
      No module named 'org'

    You may encounter a case where excluding an entire package is not possible.
    For example, in this library's ``core``, it loads an automation scope from
    openHAB. This scope must be loaded at runtime and so does not exist if you
    simply import ``core.jsr223``. So when other packages in the core try to
    import ``core.jsr223.scope`` it produces errors, but excluding ``core``
    would result in the entire package being ignored. When you need to
    exclude only a specific module you can add it to the ``MOCK_MODULES`` list.


Formatting
==========

  The following is a summary of useful reStructuredText inline markdowns and
  directives. Any of these can be used in the ``.rst`` files you create, or
  directly in the *docstrings* in your ``.py`` files. You can find examples in
  the ``core`` module.

Emphasis
--------

    * Text can be made *italic* by surrounding it with single asterisk
      ``*italic*``
    * Text can be made **bold** by surrounding it with two asterisks
      ``**bold**``
    * Inline code ``like this`` is done with two ticks: ````like this````
    * The content between these symbols may not start or end with whitespace
      ``* wrong*``

Lists
-----

    Lists are simple to create and can be bullets or number, and can also be
    nested by indenting. Numbers for numbered lists are ignored, items will be
    numbered automatically.

    .. code-block:: rest

      1. This is a numbered list

      * This is a bullet
        and can span multiple lines

      #. This is also a numbered list

         #. With a nested item

    1. This is a numbered list

    * This is a bullet
      and can span multiple lines

    #. This is also a numbered list

       #. With a nested item

Codeblocks
----------

    Codeblocks are created using the ``.. code-block:: [language]`` directive.
    The language is optional, and will default to ``python3``. Any text below
    the directive that is indented will be part of the block.

    .. code-block:: rest

      This is a normal text paragraph. The next paragraph is a code sample

      .. code-block:: rest

        It is not **processed** in any way, except
        that the indentation is removed.

        It can span multiple ``lines``.

      This is a normal text paragraph again.

Hyperlinks
----------

    External links can be made inline like this:

    .. code-block:: rest

      This file is `here <https://github.com/OH-Jython-Scripters/openhab2-jython/tree/master/Sphinx/Contributing/Writing%20Docs.rst>`_

    or separately like this:

    .. code-block:: rest

      This file is `here`_

      .. _here: https://github.com/OH-Jython-Scripters/openhab2-jython/tree/master/Sphinx/Contributing/Writing%20Docs.rst

    You can also link to other sections on any page like this:

    .. code-block:: rest

      This section is :ref:`Contributing/Writing Docs:Hyperlinks`

    or documents within this documentation:

    .. code-block:: rest

      This page is :doc:`/Contributing/Writing Docs`

Field Lists
-----------

    | Field lists are a more specific type of list that is available

    .. code-block:: rest

      :param my_arg: Description of argument
      :attr my_attr: Description of attribute
      :returns: Function return value

    Results in:

    :param my_arg: Description of argument
    :attr my_attr: Description of attribute
    :returns: Function return value

Images
------

    Images can be inserted using the following:

    .. code-block:: rest

        .. image:: Community/my_module/picture.png
            :width: 50%
            :alt: image alt text
            :align: center
            :target: http://link-to-some-page

    The options listed below the image directive are all optional.

    Any images should be put in ``/Sphinx/_static/Community/my_module/``
