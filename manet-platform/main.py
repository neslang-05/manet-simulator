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

# ── Ensured output directories exist ──────────────────────────────────────────
from backend.paths import get_data_path, get_resource_path
for d in ["outputs/history", "logs", "assets"]:
    get_data_path(d).mkdir(parents=True, exist_ok=True)

# ── Bundle Verification Mode (for automated testing) ───────────────────────
if "--check-bundle" in sys.argv:
    is_frozen = getattr(sys, "frozen", False)
    presets_path = get_resource_path("configs", "presets.json")
    sim_cpp_path = get_resource_path("ns3", "manet-sim.cc")
    
    print("=== Bundle Verification ===")
    print(f"sys.frozen: {is_frozen}")
    print(f"Presets path: {presets_path} (exists: {presets_path.exists()})")
    print(f"Sim C++ path: {sim_cpp_path} (exists: {sim_cpp_path.exists()})")
    
    if presets_path.exists() and sim_cpp_path.exists():
        print("BUNDLE_VERIFICATION: SUCCESS")
        sys.exit(0)
    else:
        print("BUNDLE_VERIFICATION: FAILED")
        sys.exit(1)

# ── Launch GUI ────────────────────────────────────────────────────────────────
from ui.app import ManetApp

if __name__ == "__main__":
    app = ManetApp()
    app.mainloop()

