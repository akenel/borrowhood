"""qa/ — QA Testing Dashboard split by concern.

Previously one 514-line qa.py. Now a package.

Exports two routers (api + html) to match main.py's existing
include_router calls: `qa.router` and `qa.html_router`.
"""

# Import submodules so their routes register on the shared routers.
from . import bugs, html, summary, tests  # noqa: F401

# Public router handles (main.py uses these).
from ._shared import router, html_router  # noqa: F401
