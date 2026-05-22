#!/bin/bash
# =============================================================================
# install.sh — Copy all MANET simulation files into ns-3-dev/scratch/ and build
#
# This script is called automatically by the Python GUI Diagnostics panel
# ("Install & Build manet-sim" button), but can also be run manually.
#
# Usage (inside WSL, from the repo ns3/ folder):
#   bash install.sh
# =============================================================================

NS3_DIR="$HOME/ns-3-dev"
SCRATCH="$NS3_DIR/scratch"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

echo "[install.sh] NS-3 dir   : $NS3_DIR"
echo "[install.sh] Scratch dir: $SCRATCH"
echo "[install.sh] Source dir : $SCRIPT_DIR"

# ── Pre-flight check ──────────────────────────────────────────────────────────
if [ ! -d "$NS3_DIR" ]; then
    echo "[install.sh] ERROR: ns-3-dev not found at $NS3_DIR"
    echo "[install.sh] Please install NS-3 first (see README.md Part 2)."
    exit 1
fi

mkdir -p "$SCRATCH"

# ── Copy all simulation C++ files ─────────────────────────────────────────────
FILES=(
    "manet-sim.cc"    # Unified simulation — used by the Python GUI
    "lab-aodv.cc"     # AODV stand-alone example
    "dsdv-manet.cc"   # DSDV stand-alone example
    "lab-dsr.cc"      # DSR  stand-alone example
    "lab-olsr.cc"     # OLSR stand-alone example
)

for FILE in "${FILES[@]}"; do
    SRC="$SCRIPT_DIR/$FILE"
    if [ -f "$SRC" ]; then
        cp "$SRC" "$SCRATCH/$FILE"
        echo "[install.sh] Copied: $FILE -> $SCRATCH/$FILE"
    else
        echo "[install.sh] WARNING: $SRC not found, skipping."
    fi
done

# ── Copy CMakeLists.txt so NS-3 builds all targets ────────────────────────────
if [ -f "$SCRIPT_DIR/CMakeLists.txt" ]; then
    cp "$SCRIPT_DIR/CMakeLists.txt" "$SCRATCH/CMakeLists.txt"
    echo "[install.sh] Copied: CMakeLists.txt -> $SCRATCH/CMakeLists.txt"
else
    echo "[install.sh] WARNING: CMakeLists.txt not found, skipping."
fi

# ── Build all scratch targets ─────────────────────────────────────────────────
cd "$NS3_DIR" || exit 1

echo ""
echo "[install.sh] Building all MANET simulations (this may take a few minutes)..."
echo ""

./ns3 build scratch/manet-sim  2>&1
BUILD_MAIN=$?

./ns3 build scratch/lab-aodv   2>&1
./ns3 build scratch/dsdv-manet 2>&1
./ns3 build scratch/lab-dsr    2>&1
./ns3 build scratch/lab-olsr   2>&1

echo ""
if [ $BUILD_MAIN -eq 0 ]; then
    echo "[install.sh] ✓ manet-sim (GUI simulation) built successfully."
    echo "[install.sh] ✓ Protocol examples built."
    echo "[install.sh] Installation complete — you can now run simulations from the GUI."
else
    echo "[install.sh] ✗ Build failed. Check errors above."
    echo "[install.sh] Tip: Make sure all NS-3 dependencies are installed (see README Part 2.1)."
    exit 1
fi
