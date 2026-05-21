#!/bin/bash

# ----------------------------
# OLSR Simulation Runner
# ----------------------------

NS3_DIR="$HOME/ns-3-dev"
NETANIM_DIR="$HOME/netanim/build"
ANIM_FILE="olsr-animation.xml"
ORIGIN_DIR="$PWD"

echo "Running OLSR Simulation from: $ORIGIN_DIR"

cd "$NS3_DIR" || { echo "ns-3 directory not found"; exit 1; }

# Run simulation
./ns3 run lab-olsr

# Copy the generated animation file back to your Windows folder
if [ -f "$ANIM_FILE" ]; then
    echo "Copying $ANIM_FILE back to your project folder..."
    cp "$ANIM_FILE" "$ORIGIN_DIR/"
fi

# Check if animation file exists
if [ -f "$ANIM_FILE" ]; then
    echo "Opening NetAnim... (Close the NetAnim window to exit this script)"
    cd "$NETANIM_DIR" || { echo "NetAnim directory not found"; exit 1; }
    ./netanim "$NS3_DIR/$ANIM_FILE"
else
    echo "Animation file not found. Check simulation code."
fi
