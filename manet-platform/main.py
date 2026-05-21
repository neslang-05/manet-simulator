"""
main.py — MANET Research & Visualization Platform Entry Point

Usage:
    python main.py

Requirements:
    pip install customtkinter matplotlib pandas numpy Pillow
"""

import sys
import os

# ── Add project root to path ──────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Dependency check ──────────────────────────────────────────────────────────
def check_dependencies():
    missing = []
    for pkg in ["customtkinter", "matplotlib", "pandas", "numpy", "PIL"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg if pkg != "PIL" else "Pillow")
    return missing


missing = check_dependencies()
if missing:
    print(f"[ERROR] Missing Python packages: {', '.join(missing)}")
    print(f"[FIX]   Run: pip install {' '.join(missing)}")
    sys.exit(1)

# ── Ensure output directories exist ──────────────────────────────────────────
from pathlib import Path
for d in ["outputs/history", "logs", "assets"]:
    Path(ROOT, d).mkdir(parents=True, exist_ok=True)

# ── Launch GUI ────────────────────────────────────────────────────────────────
from ui.app import ManetApp

if __name__ == "__main__":
    app = ManetApp()
    app.mainloop()
