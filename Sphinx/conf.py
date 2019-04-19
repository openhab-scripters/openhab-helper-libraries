# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('./../Core/automation/lib/python'))


# -- Mock setup --------------------------------------------------------------

# allows autodoc to import modules that import things that Sphinx/RTD can't import

import mock

# list of modules to spoof
# all java and dynamic modules that Sphinx won't be able to load in
# a normal python env
MOCK_MODULES = ['core.jsr223.scope',
    'org', 'org.joda', 'org.joda.time',
    'java', 'java.util', 'java.time', 'java.time.format', 'java.time.temporal', 'java.time.temporal.ChronoUnit',
    'org.openhab', 'org.openhab.core', 'org.openhab.core.library', 'org.openhab.core.library.types',
    'org.eclipse', 'org.eclipse.smarthome', 'org.eclipse.smarthome.core', 'org.eclipse.smarthome.core.library',
    'org.eclipse.smarthome.core.library.types'
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = mock.Mock()


# -- Project information -----------------------------------------------------

project = 'openHAB Scripters - Jython'
author = 'Scott Rushworth, Mike Murton'
copyright = '2019, Scott Rushworth, Mike Murton'
version = 'latest'


# -- General configuration ---------------------------------------------------

# Master document file, must contain 'toctree' directive
master_doc = 'index'

# Default code-block language highlighting to use
highlight_language = 'python'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Source file extensions and the parser to be used
source_suffix = {
    '.rst': 'restructuredtext'
}

# A string of reStructuredText that will be included at the end of every
# source file that is read. This is a possible place to add substitutions
# that should be available in every file
rst_epilog = """"""

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for autodoc -----------------------------------------------------

# shows class and __init__ docstrings
autoclass_content = 'both'

# sorts class/func/attr in order found in code
autodoc_member_order = 'bysource'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = ["_themes", ]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Logo image to put at the top of the sidebar (max width 200px)
#html_logo = '_static/logo.png'

# HTML page/tab icon
#html_favicon = '_static/favicon.ico'