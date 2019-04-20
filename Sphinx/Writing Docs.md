# Writing Docs

  This document will show you how to format python docstrings using reStructuredText
  and what files you need to create so that Sphinx will pull the docstrings from
  your module. There are also instructions on how to setup Sphinx to build the
  docs so that you can verify that your documentation is rendering correctly.
  
## Docstrings

  Python docstrings

### Where to put docstrings

  beginning of single-file or `__init__.py` for folder  
  above or below class/func/attr
  inline one-liner for attr

#### File Header

  `:Authors: Your Name; Someone else`
  `:Organization: openHAB Scripters`

## reStructuredText

### reST Basics

#### Paragraphs

  Paragraphs are simply separated by one or more lines, and will render with a
  single blank line between them. All lines of a paragraph must be at the same
  indentation level, like python code.

#### Emphasis

  * Text can be made *italic* by surrounding it with single asterisks: `*italic*`
  * Text can be made **bold** by surrounding it with two asterisks: `**bold**`
  * Inline code `like this` is done with two ticks: ` ``like this`` `  

  The content between these symbols may not start or end with whitespace:
  `* wrong*`

#### Codeblocks

  Codeblocks are created by placing `::` at the end of a paragraph. If there is
  no whitespace before `::` then a single `:` will be rendered, if there is
  whitespace before then it will be hidden.

  ```reST
    This is a normal text paragraph. The next paragraph is a code sample::

      It is not processed in any way, except
      that the indentation is removed.

      It can span multiple lines.

    This is a normal text paragraph again.
  ```

#### Hyperlinks

  External links can be made inline like this:

  ```reST
    This file is `here <https://github.com/OH-Jython-Scripters/openhab2-jython/tree/master/Sphinx/Writing-Docs.md>`_
  ```

  or separately like this:

  ```reST
    This file is `here`_

    .. _here: https://github.com/OH-Jython-Scripters/openhab2-jython/tree/master/Sphinx/Writing-Docs.md
  ```

  You can also link to other sections or documents within this documentation if
  needed. Details about how to do this can be found in the [Sphinx Documentation](http://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#ref-role)

#### Field Lists

  Field lists should be used to detail class and function arguments and returns.
  They should also be used to detail class and module attributes.

  ```reST
    :param my_arg: Description of argument
    :attr my_attr: Description of attribute
    :returns: Function return value
  ```

#### Images

  Images can be inserted using the following on a line on its own

  ```reST
    .. image:: picture.png
        :width: 50%
        :alt: image alt text
        :align: center
        :target: http://link-to-some-page
  ```

  The options listed below the image directive are all optional

## Adding Documentation for a Module

  When you are contributing a new module to this repo you need to add a simple
  reST file (`.rst`) to allow Sphinx to extract the Python docstrings from your module. This
  file must have the same name as your module, whether your module is a folder
  or just a single file.  

  ***A warning about Sphinx autodoc:***  
  *autodoc is also written in python and will import your module. This means that
  any imports or code that runs when loaded will happen when it does this.  
  In particular for this library, it means that autodoc will throw errors when
  trying to import openHAB classes, the solution to this is outlined in
  [Building the docs](#building-the-docs)*

### Single Page Module Documentation

  If your module requires only a single page of documentation, you will only need
  to create one reST file. This file must have the same name as your module (eg.
  `my_module.rst`) to avoid naming conflicts with other modules, and be in the
  `lib/python/community/` directory with your module.

  Below is an example of what is required in this file:

  ```reST
    Example Module
    ==============

    .. automodule:: my_module.py
        :members:

  ```

  * The heading is the name of your module as it should appear in the documentation,
    the `===` line below it must be at least the same length as the heading.
  * `automodule` instructs Sphinx to parse `my_module.py`.
  * `:members:` is optional and tells Sphinx to only extract docstrings from visible
    functions, classes, and attributes (everything in `__all__`, if specified).  
    You can also specify explicitly which members should be parsed by adding them as a
    list after the directive, eg. `:members: func1, func2, attr1, class1`.
  * Note the trailing empty line, all `.rst` files must end with a blank line

  You should now have the following files in the `lib/python/community` directory
  relating to your module. You should now go the [Building the docs](#building-the-docs)
  section and make sure your documentation is compiling and rendering correctly.

  ```bash
    lib/python/community/my_module.py
    lib/python/community/my_module.rst
  ```

  More advanced parsing options are documented [here](http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
  if you need them.

### Multi-Page Module Documentation

  It is also possible for each file of a multi-file module to have its own page
  in the docs.
  
  1. Create an `.rst` file for each file in your module and place it in the
     module directory, using the content for a single page module.  
     Use `---` instead of `===` under the heading.
  2. Then create an `.rst` file in the `lib/python/community/` directory with the
     same name as your module directory, with the following content:

     ```reST
      Example Multi-Page Module
      =========================

      .. automodule: my_module

      .. toctree::
          :maxdepth: 1
          :glob:

          my_module/*

     ```

     * The heading is the name of your module as it should appear in the documentation,
       the `===` line below it must be at least the same length as the heading.
     * `.. automodule: my_module` will pull the docstring from your module's
       `__init__.py` for only the module
     * `:caption:` should be followed by the name of your module again, use this
       only if you are using `.. automodule:``
     * `:maxdepth:` should always be `1`
     * `:glob:` tells Sphinx to look for any `.rst` files in the directories below
     * `my_module/*` should be changed to the name of your module follow by `/*`
       so that Sphinx will look for any `.rst` file in the directory.  
       If your module contains subdirectories, you will need to list them here as
       well. They will be scanned for files in the order you put them, and any files
       found will be displayed in alphabetical order.
     * Note the trailing empty line, all `.rst` files must end with a blank line

  You should now have files similar to the following in the `lib/python/community` directory
  relating to your module. You should now go the [Building the docs](#building-the-docs)
  section and make sure your documentation is compiling and rendering correctly.

  ```bash
    lib/python/community/my_module.rst
    lib/python/community/my_module/__init__.py
    lib/python/community/my_module/my_file.py
    lib/python/community/my_module/my_file.rst
  ```

## Building the Docs

  Setup venv and build