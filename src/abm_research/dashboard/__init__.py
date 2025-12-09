"""
ABM Dashboard Module (Consolidated)

The dashboard has been consolidated:
- React frontend: /dashboard/
- Flask API: /src/abm_research/api/server.py

Legacy dashboard files have been archived to /archive/legacy-dashboards/
"""

# Re-export from new location for backwards compatibility
from ..api.server import app
