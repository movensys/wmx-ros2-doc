# -- Project information -----------------------------------------------------
project = 'WMX R2 Documentation'
copyright = '2026, MOVENSYS'
author = 'MOVENSYS'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',           # Markdown support
    'sphinx.ext.autodoc',    # Auto-generate from docstrings
    'sphinx.ext.intersphinx',# Cross-reference other Sphinx docs
    'sphinx.ext.todo',       # TODO directives
    'sphinxcontrib.mermaid', # Mermaid diagram support
    'sphinx_design',         # Tabs, cards, grids
]

# Markdown support
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

rst_prolog = """
.. role:: bi
.. role:: red
"""

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_redirects']

# -- Redirects ---------------------------------------------------------------
# Copied verbatim into the build output. GitHub Pages is deployed with
# ``keep_files: true``, so a page that is renamed keeps serving its old, stale
# HTML at the old URL forever. A stub here overwrites it with a redirect.
#
#   examples/Testing WMX R2.html -> examples/testing_wmx_r2.html
#
# Add a stub whenever a published page is renamed or moved.
html_extra_path = ['_redirects']

# -- Mermaid ----------------------------------------------------------------
# Render diagrams at their natural size instead of clamping every SVG to the
# content-column width (mermaid's default ``useMaxWidth: true``), which shrinks
# wide graphs until the text is unreadable. With this off, the SVG carries
# pixel width/height and custom.css lets it scroll horizontally when needed.
mermaid_init_config = {
    "startOnLoad": False,
    "flowchart": {"useMaxWidth": False},
    "sequence": {"useMaxWidth": False},
}

# -- Options for HTML output -------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

html_logo = '_static/movensys_logo.png'
html_favicon = '_static/movensys_logo.png'

html_show_sourcelink = False
html_last_updated_fmt = '%b %d, %Y'

html_theme_options = {
    "logo": {
        "text": "WMX R2 Documentation",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/movensys/wmx-r2-doc",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    "navbar_align": "left",
    "navigation_depth": 2,
    "show_nav_level": 1,
    "show_toc_level": 2,
    "collapse_navigation": True,
    "navbar_start": ["navbar-logo"],
    "navbar_center": [],
    "navbar_end": ["search-button", "navbar-icon-links"],
    "primary_sidebar_end": [],
    "sidebar_includehidden": True,
    "footer_start": [],
    "footer_end": [],
    "secondary_sidebar_items": ["page-toc"],
}

html_sidebars = {
    "**": ["sidebar-toc-header", "sidebar-nav-global"],
}

html_context = {
    "default_mode": "light",
}

# -- Intersphinx mapping (link to ROS2 docs) --------------------------------
# Left empty intentionally: no page currently uses an ``:external+ros2:`` /
# ``ros2:`` cross-reference, and fetching docs.ros.org/en/humble/objects.inv at
# build time is unreliable (the host serves an anti-bot challenge page instead
# of the inventory), which fails the strict ``-W`` build. To re-enable ROS2
# cross-references, add the mapping back with a committed local inventory
# fallback, e.g. ('https://docs.ros.org/en/humble/', (None, '_inv/ros2.inv')).
intersphinx_mapping = {}

# -- Options for linkcheck builder ------------------------------------------
# The WMX3 installer downloads sit behind WebDAV basic auth (guest/guest)
# that the linkcheck HEAD probe cannot satisfy, so skip them.
linkcheck_ignore = [
    r'^http://download\.movensys\.com:8111/.*',
    # SharePoint download links require authentication; linkcheck cannot reach them.
    r'^https://softservogroup.*\.sharepoint\.com/.*',
]
