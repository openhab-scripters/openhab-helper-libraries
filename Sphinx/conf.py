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
import os, sys
sys.path.append(os.path.abspath('./imports/lib/python'))
sys.path.append(os.path.abspath('./imports/jsr223/python'))
sys.path.append(os.path.abspath('./imports/examples/Python'))

# -- Project information -----------------------------------------------------

project = 'openHAB Helper Libraries'
author = 'Contributors to the openHAB Scripters project'
copyright = '2019, Contributors to the openHAB Scripters project'
version = 'latest'


# -- General configuration ---------------------------------------------------

# Master document file, must contain 'toctree' directive
master_doc = 'index'

# Default code-block language highlighting to use
highlight_language = 'python'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'vscode'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx_tabs.tabs'
]

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
#autoclass_content = 'both'

# autodoc default options for directives
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'show-inheritance': True
}

# base modules that should be mock'd
autodoc_mock_imports = ['org', 'java', 'configuration']

# -- Mock --------------------------------------------------------------------

# allows autodoc to import modules that import things that Sphinx can't import

import mock

# list of modules to spoof
# use this only for specific imports that arent working. entire modules can be
# spoofed using autodoc_mock_imports in the section above
MOCK_MODULES = [
    'core.jsr223.scope',
    'core.JythonItemProvider',
    'core.JythonItemChannelLinkProvider',
    'core.JythonExtensionProvider',
    'TriggerHandlerFactory',
    'ActionHandler',
    'ActionType',
    'Visibility',
    'ConfigDescriptionParameter',
    'ConfigDescriptionParameterBuilder',
    'automationManager',
    'core.rules_mock',
    'core.triggers_mock',
    'core.actions_mock',
    'core.date_mock',
    'personal.idealarm',
    'com.espertech.esper.client',
    'meteocalc',
    'urllib2',
    'StringIO',
    'scriptExtension'
]
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = mock.Mock()

# -- Options for autosectionlabel --------------------------------------------

# prefixes sections with doc and a colon
# ex installation:package
autosectionlabel_prefix_document = True


# -- Options for HTML output -------------------------------------------------

# root url for these docs, also used to make CNAME for GH Pages
html_baseurl = "https://openhab-scripters.github.io/openhab-helper-libraries/"

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

# Disable "View Page Source" header link
html_show_sourcelink = False

# RTD Theme options
html_theme_options = {
    'canonical_url': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': None,
    'style_external_links': True,
    'style_nav_header_background': None,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': False,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}
html_context = {
    # Enable the "Edit in GitHub link within the header of each page.
    'display_github': True,
    # Set the following variables to generate the resulting github URL for each page.
    # Format Template: https://{{ github_host|default("github.com") }}/{{ github_user }}/{{ github_repo }}/blob/{{ github_version }}{{ conf_py_path }}{{ pagename }}{{ suffix }}
    'github_user': 'openhab-scripters',
    'github_repo': 'openhab-helper-libraries',
    'github_version': 'master/',
    'conf_py_path': 'Sphinx/',
    'suffix': '.rst'
}
