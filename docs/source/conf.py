# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Dopyqo'
copyright = '2026, Erik Schultheis, Alexander Rehn, Erik Hansen, Jasper Nickelsen, Gabriel Breuil'
author = 'Erik Schultheis, Alexander Rehn, Erik Hansen, Jasper Nickelsen, Gabriel Breuil'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_design',
]

templates_path = ['_templates']
exclude_patterns = []

# Suppress docutils RST-parsing warnings from package docstrings (|math| pipe notation
# and multi-line arg indentation). These should be fixed by converting inline math to
# :math:`...` roles and block math to .. math:: directives.
suppress_warnings = ['docutils']

autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# Packages that cannot or should not be installed in the ReadTheDocs build
# environment (GPU-only, heavy compiled extensions, or slow to install).
# Sphinx replaces these with MagicMock objects so autodoc can still parse
# all type annotations and docstrings that reference them.
autodoc_mock_imports = [
    "cupy",
    "numba",
    "h5py",
    "pyscf",
    "tencirchem",
    "qiskit",
    "qiskit_nature",
    "qiskit_algorithms",
    "pyvista",
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pyscf': ('https://pyscf.org/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'shibuya'
html_static_path = ['_static']

html_theme_options = {
    "github_url": "https://github.com/dlr-wf/Dopyqo",
}
