#!/bin/bash
# install.sh — Copy manet-sim.cc into ns-3-dev scratch folder

NS3_DIR="$HOME/ns-3-dev"
SCRATCH="$NS3_DIR/scratch"
SRC="$(dirname "$(readlink -f "$0")")/manet-sim.cc"

echo "[install.sh] NS-3 dir: $NS3_DIR"

if [ ! -d "$NS3_DIR" ]; then
    echo "ERROR: ns-3-dev not found at $NS3_DIR"
    exit 1
fi

mkdir -p "$SCRATCH"
cp "$SRC" "$SCRATCH/manet-sim.cc"
echo "[install.sh] Copied manet-sim.cc -> $SCRATCH/manet-sim.cc"

cd "$NS3_DIR" || exit 1
echo "[install.sh] Building manet-sim..."
./ns3 build scratch/manet-sim 2>&1
if [ $? -eq 0 ]; then
    echo "[install.sh] Build successful!"
else
    echo "[install.sh] Build failed. Check errors above."
    exit 1
fi
