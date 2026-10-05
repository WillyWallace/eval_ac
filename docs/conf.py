"""Sphinx configuration of the eval_ac documentation."""
# pylint: disable=invalid-name
import eval_ac

project = 'eval_ac'
author = eval_ac.__author__
copyright = f'2022-2026, {author}'  # pylint: disable=redefined-builtin
release = eval_ac.__version__
version = release

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}
exclude_patterns = ['_build']

# anchors for headings, so that links like [Drift plot](#drift-plot) from
# the included README work
myst_heading_anchors = 4
# the README sections start at heading level 3
suppress_warnings = ['myst.header']

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'xarray': ('https://docs.xarray.dev/en/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

html_theme = 'furo'
html_title = f'eval_ac {release}'
