#!/usr/bin/env python3
# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options.
# For a full list see the documentation:
#   http://www.sphinx-doc.org/en/master/config
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import time

# -- Path setup -----------------------------------------------------
# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory
# is relative to the documentation root, use os.path.abspath to make
# it absolute, like shown here.

sys.path.insert(0, os.path.abspath(__file__))

from skeleton.__version__ import (
  __author__,
  __title__,
  __version__,
  __description__
)

# -- Project information --------------------------------------------

project, author = __title__, __author__

# noinspection PyShadowingBuiltins
copyright = '%s, %s' % (author, time.strftime('%Y'))
version = '%s.' % __version__.split(".")[:-1]  # Short X.Y version.
release = __version__  # Full version, including alpha/beta/rc tags

# -- General configuration ------------------------------------------

# Add any Sphinx extension module names here, as strings. They can
# be extensions coming with Sphinx (named 'sphinx.ext.*') or your
# custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
    'guzzle_sphinx_theme'
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

todo_include_todos = True

# Add any paths that contain templates here, relative to this
# directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files
# and directories to ignore when looking for source files. This
# pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ----------------------------------------

# The theme to use for HTML and HTML Help pages.  See the
# documentation for a list of builtin themes.
# html_theme = 'default'

# Add any paths that contain custom static files (such as style
# sheets) here, relative to this directory. They are copied after
# the builtin static files, so a file named "default.css" will
# overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, maps document names to template names.
html_show_sourcelink = False

# Custom sidebar templates, filenames relative to this file.
html_sidebars = {
    '**': [
        'logo-text.html',
        'globaltoc.html',
        'localtoc.html',
        'searchbox.html'
    ]
}

# Output file base name for HTML help builder.
htmlhelp_basename = '%sdoc' % project

# If not '', a 'Last updated on:' timestamp is inserted at
# every page bottom, using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

import guzzle_sphinx_theme

html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = 'guzzle_sphinx_theme'

# -- Options for LaTeX output ---------------------------------------

latex_elements = {
    # Paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    #
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    #
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author,
# documentclass [howto/manual]).
latex_documents = [
    ('index', '%s.tex' % project, '%s Documentation' % project,
     author, 'manual')
]

# The name of an image file (relative to this directory) to place at
# the top of the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings
# are parts, not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True

# -- Options for manual page output ---------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', project, '%s Documentation' % project, [author], 3)
]

# If true, show URL addresses after external links.
# man_show_urls = False

# -- Options for Texinfo output -------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)

texinfo_documents = [
    ('index', project, '%s Documentation' % project, author, project,
     __description__, 'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

autoclass_content = 'both'
