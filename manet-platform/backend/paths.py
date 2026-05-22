"""
backend/paths.py — Centralized path resolution for frozen & non-frozen environments.
"""

import sys
import os
from pathlib import Path

IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    # In PyInstaller, resource files are unpacked to sys._MEIPASS
    RESOURCE_ROOT = Path(sys._MEIPASS)
    # Writeable data goes to the directory where the .exe is located
    DATA_ROOT = Path(os.path.dirname(sys.executable))
else:
    # Non-frozen: resource and data root is the manet-platform directory
    # paths.py is at manet-platform/backend/paths.py, so parent.parent is manet-platform
    RESOURCE_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
    DATA_ROOT = RESOURCE_ROOT

def get_resource_path(*parts) -> Path:
    """Get path to a read-only bundled resource file."""
    return RESOURCE_ROOT.joinpath(*parts)

def get_data_path(*parts) -> Path:
    """Get path to a writeable user data file or directory."""
    return DATA_ROOT.joinpath(*parts)
