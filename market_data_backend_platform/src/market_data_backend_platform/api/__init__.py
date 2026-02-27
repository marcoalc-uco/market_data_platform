# API module
"""API module containing routes and dependencies.

This module provides the HTTP API layer:
- routes: Endpoint definitions organized by domain
- dependencies: Shared FastAPI dependencies for injection
"""

from .dependencies import SettingsDep

__all__ = ["SettingsDep"]
