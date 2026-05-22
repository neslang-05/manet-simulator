# MANET Simulator

> **Mobile Ad-hoc Network Simulation & Visualization Platform**
> combining NS-3, NetAnim, Python/CustomTkinter, and WSL2 Ubuntu.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![NS-3](https://img.shields.io/badge/NS--3-3.x-green)](https://www.nsnam.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2011%20%2B%20WSL2-0078D4?logo=windows)](https://learn.microsoft.com/en-us/windows/wsl/)
[![License](https://img.shields.io/badge/License-Academic-lightgrey)](./LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [System Requirements](#system-requirements)
- [Part 1 — WSL2 & Ubuntu Setup](#part-1--wsl2--ubuntu-setup)
- [Part 2 — NS-3 Installation (inside WSL)](#part-2--ns-3-installation-inside-wsl)
- [Part 3 — NetAnim Installation (inside WSL)](#part-3--netanim-installation-inside-wsl)
- [Part 4 — Clone & Python Setup (Windows)](#part-4--clone--python-setup-windows)
- [Part 5 — Install the NS-3 Simulation File](#part-5--install-the-ns-3-simulation-file)
- [Running the GUI Platform](#running-the-gui-platform)
- [Running Simulations via Shell Scripts](#running-simulations-via-shell-scripts)
- [Simulation Configuration Parameters](#simulation-configuration-parameters)
- [Supported Protocols](#supported-protocols)
- [Generated Outputs](#generated-outputs)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project provides two ways to run MANET protocol simulations:

| Mode | Description |
|---|---|
| **GUI Platform** | Full Python desktop app — configure, run, and visualize simulations interactively |
| **Shell Scripts** | Lightweight bash scripts for direct NS-3 execution and NetAnim visualization |

Both modes require **NS-3 installed inside WSL2** on your Windows machine.

---

## Architecture

```
manet-simulator/
├── README.md
├── .gitignore
│
├── run_aodv.sh          # Direct NS-3 runner for AODV
├── run_dsdv.sh          # Direct NS-3 runner for DSDV
├── run_dsr.sh           # Direct NS-3 runner for DSR
├── run_olsr.sh          # Direct NS-3 runner for OLSR
│
└── manet-platform/      # Python GUI application
    ├── main.py          # Entry point  ← launch this
    ├── requirements.txt
    ├── ui/              # CustomTkinter interface (7 panels)
    ├── backend/         # WSL bridge, simulation runner, experiment manager
    ├── ns3/
    │   ├── manet-sim.cc # Unified NS-3 C++ simulation source
    │   └── install.sh   # Copies & builds manet-sim inside WSL
    ├── analysis/        # CSV parsing, graph generation, comparison engine
    ├── configs/         # Default parameters and named presets
    └── outputs/         # Auto-created — timestamped simulation results
```

---

## System Requirements

| Component | Requirement |
|---|---|
| **OS** | Windows 10 (version 2004+) or Windows 11 |
| **WSL Version** | WSL2 (not WSL1) |
| **Linux Distro** | Ubuntu 20.04 or 22.04 (inside WSL2) |
| **Python** | 3.10 or newer **(on Windows)** |
| **NS-3** | Installed at `~/ns-3-dev` inside WSL |
| **NetAnim** | Installed at `~/netanim` inside WSL |
| **RAM** | 8 GB minimum, 16 GB recommended |
| **Disk** | ~5 GB free for NS-3 build |

---

## Part 1 — WSL2 & Ubuntu Setup

> Skip this part if you already have WSL2 + Ubuntu running.

### 1.1 Enable WSL2

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

This installs WSL2 with Ubuntu by default. **Restart your PC** when prompted.

### 1.2 Verify WSL2 is active

```powershell
wsl --list --verbose
```

You should see your Ubuntu distro listed with `VERSION 2`. If it shows version 1, upgrade it:

```powershell
wsl --set-version Ubuntu 2
```

### 1.3 Open Ubuntu

Launch **Ubuntu** from the Start menu (or run `wsl` in PowerShell). Complete the first-time username/password setup.

### 1.4 Update Ubuntu packages

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Part 2 — NS-3 Installation (inside WSL)

> All commands in this section run **inside the WSL/Ubuntu terminal**.

### 2.1 Install build dependencies

```bash
sudo apt install -y \
  g++ python3 python3-pip cmake ninja-build git \
  libsqlite3-dev libxml2-dev libgtk-3-dev \
  libboost-all-dev mercurial gsl-bin libgsl-dev \
  qt5-default libqt5svg5-dev qtbase5-dev
```

> **Ubuntu 22.04 note:** Replace `qt5-default` with `qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools`

### 2.2 Clone the NS-3 repository

```bash
cd ~
git clone https://gitlab.com/nsnam/ns-3-dev.git ns-3-dev
cd ns-3-dev
```

### 2.3 Configure and build NS-3

```bash
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

> ⚠️ This step takes **15–40 minutes** depending on your machine. Do not interrupt it.

### 2.4 Verify the build

```bash
./ns3 run hello-simulator
```

Expected output:
```
Hello Simulator
```

---

## Part 3 — NetAnim Installation (inside WSL)

> NetAnim is a graphical animation viewer for NS-3 simulation traces.

### 3.1 Install Qt dependencies (if not already done)

```bash
sudo apt install -y qt5-default libqt5svg5-dev
# Ubuntu 22.04:
# sudo apt install -y qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5svg5-dev
```

### 3.2 Clone and build NetAnim

```bash
cd ~
git clone https://gitlab.com/nsnam/netanim.git
cd netanim
qmake NetAnim.pro
make -j$(nproc)
```

### 3.3 Verify NetAnim

```bash
~/netanim/build/netanim --version
```

If you see version output (or the GUI opens), NetAnim is ready.

---

## Part 4 — Clone & Python Setup (Windows)

> These commands run in **Windows PowerShell or Command Prompt**.

### 4.1 Clone the repository

```powershell
git clone https://github.com/neslang-05/manet-simulator.git
cd manet-simulator
```

### 4.2 Install Python dependencies

```powershell
pip install -r manet-platform/requirements.txt
```

This installs:

| Package | Version | Purpose |
|---|---|---|
| `customtkinter` | ≥ 5.2.0 | Modern GUI framework |
| `matplotlib` | ≥ 3.7.0 | Graph generation |
| `pandas` | ≥ 2.0.0 | CSV data processing |
| `numpy` | ≥ 1.24.0 | Numerical computations |
| `Pillow` | ≥ 10.0.0 | Image handling in GUI |

### 4.3 Confirm Python version

```powershell
python --version
```

Must be **3.10 or higher**.

---

## Part 5 — Install the NS-3 Simulation File

The GUI platform uses a unified NS-3 simulation file (`manet-sim.cc`) that must be copied into NS-3's scratch directory and compiled inside WSL.

### Option A — Via the GUI (Recommended)

1. Launch the platform: `python manet-platform/main.py`
2. Navigate to the **Diagnostics** panel (bottom of the left sidebar)
3. Click **"Install & Build manet-sim"**
4. Wait for the build to complete — the console will show `[install.sh] Build successful!`

### Option B — Manually via WSL terminal

Open **Ubuntu (WSL)** and run:

```bash
# Find where Windows cloned the repo (adjust the path to your username)
REPO_PATH="/mnt/c/Users/<YourWindowsUsername>/manet-simulator"

# Copy the simulation file into NS-3 scratch
cp "$REPO_PATH/manet-platform/ns3/manet-sim.cc" ~/ns-3-dev/scratch/

# Build it
cd ~/ns-3-dev
./ns3 build scratch/manet-sim
```

Expected output ends with:
```
[install.sh] Build successful!
```

---

## Running the GUI Platform

```powershell
cd manet-simulator
python manet-platform/main.py
```

The application opens with 7 panels accessible from the left sidebar:

| Panel | Description |
|---|---|
| **Simulation** | Configure parameters and launch a simulation |
| **Console** | Real-time log output from NS-3 |
| **Results** | Metric dashboard (PDR, throughput, delay, energy) |
| **Graphs** | View auto-generated PNG plots |
| **History** | Browse and re-run past experiments |
| **Comparison** | Side-by-side protocol comparison |
| **Diagnostics** | WSL health check, NS-3 build, environment info |

### Quick Start Workflow

```
1. Open Simulation panel
2. Select a protocol (AODV / DSDV / DSR / OLSR)
3. Adjust parameters or pick a preset
4. Click "Run Simulation"
5. Watch Console for live NS-3 output
6. View results in Results → Graphs panels
```

---

## Running Simulations & NetAnim step-by-step for Each Algorithm

Each of the four routing algorithms (AODV, DSDV, DSR, OLSR) can be simulated and visualized either via the **GUI Platform** or **Shell Scripts** inside WSL. Below are the step-by-step instructions.

### 1. Verification of Simulation Binaries
Before running, make sure the compilation targets for each algorithm are built inside NS-3. 
- **Automatic**: Click **"Install & Build Sim"** on the GUI Simulation or Diagnostics panel. It copies and compiles all files.
- **Manual**: Run `bash manet-platform/ns3/install.sh` in WSL. This compiles:
  - `manet-sim` (Unified simulator for GUI)
  - `lab-aodv` (AODV stand-alone)
  - `dsdv-manet` (DSDV stand-alone)
  - `lab-dsr` (DSR stand-alone)
  - `lab-olsr` (OLSR stand-alone)

---

### 2. Running Simulations Step-by-Step

#### Method A: Via the Python GUI Platform (Recommended)
1. Open Windows Terminal/PowerShell and run:
   ```powershell
   python manet-platform/main.py
   ```
2. Navigate to the **Simulation** configuration panel.
3. Choose the desired routing protocol from the dropdown menu (e.g., **AODV**).
4. Set the parameters (number of nodes, speed, simulation time, area, energy capacity, etc.) or click one of the presets.
5. Click the green **"Run Simulation"** button. The app will navigate to the Console panel, where you can watch NS-3 build/execute output in real-time.
6. Once complete, NetAnim will automatically launch with the generated XML animation file (e.g., `outputs/<timestamp>/manet-animation.xml`), and the Graphs panel will display the analyzed results.

#### Method B: Via CLI/Shell Scripts (Standalone Mode)
If you prefer running the raw simulation scripts:
1. Open the **WSL/Ubuntu terminal**.
2. Navigate to your cloned repository path:
   ```bash
   cd /mnt/c/Users/<YourWindowsUsername>/manet-simulator
   ```
3. Run the shell script corresponding to the algorithm you wish to simulate:
   - **AODV**: `bash run_aodv.sh` (runs `lab-aodv.cc`, generates `aodv-animation.xml`)
   - **DSDV**: `bash run_dsdv.sh` (runs `dsdv-manet.cc`, generates `dsdv-animation.xml`)
   - **DSR**: `bash run_dsr.sh` (runs `lab-dsr.cc`, generates `dsr-animation.xml`)
   - **OLSR**: `bash run_olsr.sh` (runs `lab-olsr.cc`, generates `olsr-animation.xml`)
4. The script will execute the NS-3 simulation, copy the animation XML file back into your main workspace directory, and automatically launch **NetAnim** pointing to that XML file.

---

### 3. Setting Up NetAnim Visualization (Step-by-Step)
Once NetAnim launches, configure the visual playback for optimal observation:

1. **Load the Animation File**:
   - If NetAnim did not auto-load the trace, click the **Open folder/file icon** (top-left of the NetAnim toolbar).
   - In the file dialog, navigate to the simulation output directory and select the generated XML trace file (e.g., `aodv-animation.xml`, `dsdv-animation.xml`, or `manet-animation.xml`).
2. **Adjust Node Display Sizes**:
   - By default, nodes might appear extremely small or large depending on your screen resolution.
   - Locate the **Node Size** slider or numeric field in the top toolbar (usually defaults to 1.0 or 2.0).
   - Set the Node Size to **5.0 or 10.0** to make the nodes clearly visible.
3. **Control Update Rate (Speed)**:
   - Use the **Update Rate (s)** slider in the top toolbar to adjust how fast the simulation runs.
   - For a 60-second simulation, setting the update rate to **0.1s** or **0.05s** provides a smooth, observable playback speed.
4. **Enable Packet Transmission Visuals**:
   - To visualize routing packets (request/reply transmissions) and data packet hops, check the **"Packets"** or **"Packet Transmission"** checkboxes in the left/top settings.
   - This will draw color-coded lines and arrows between nodes when they transmit packets (e.g., blue lines for routing overhead, green/red for data transmissions).
5. **Start Playback**:
   - Click the green **Play (Right Arrow)** button in the top left.
   - You will see the mobile nodes moving according to the configured mobility model (Random Waypoint) and transmitting packets dynamically. Use the pause/stop buttons to inspect specific events.

---

## Simulation Configuration Parameters

These parameters are configurable from the **Simulation panel** in the GUI:

| Parameter | Range | Default | Description |
|---|---|---|---|
| **Protocol** | AODV, DSDV, DSR, OLSR | AODV | Routing protocol to simulate |
| **Number of Nodes** | 5 – 100 | 20 | Total mobile nodes in the network |
| **Simulation Time** | 10 – 600 s | 60 s | How long the simulation runs |
| **Area Width** | 200 – 5000 m | 1000 m | Network area width |
| **Area Height** | 200 – 5000 m | 1000 m | Network area height |
| **Node Speed** | 1 – 50 m/s | 10 m/s | Maximum mobility speed |
| **Pause Time** | 0 – 30 s | 2 s | Duration nodes stay stationary |
| **Battery Capacity** | 10 – 500 J | 100 J | Energy per node |
| **TX Range** | 50 – 1000 m | 250 m | Transmission range |
| **Packet Size** | 64 – 4096 bytes | 512 bytes | UDP payload size |
| **Data Rate** | 512K – 10 Mbps | 2 Mbps | Application data rate |

### Built-in Presets

| Preset | Nodes | Area | Protocol | Notes |
|---|---|---|---|---|
| Small Network | 10 | 500 × 500 m | AODV | Good for quick tests |
| Medium Network | 30 | 1500 × 1500 m | OLSR | Balanced scenario |
| Large Network | 50 | 2000 × 2000 m | DSDV | Dense topology |
| Energy Stress Test | 40 | 1000 × 1000 m | AODV | Low battery, high drain |
| High Mobility | 25 | 1000 × 1000 m | DSR | 30 m/s node speed |

---

## Supported Protocols

| Protocol | Full Name | Type | Best For |
|---|---|---|---|
| **AODV** | Ad-hoc On-demand Distance Vector | Reactive | Sparse, dynamic networks |
| **DSDV** | Destination-Sequenced Distance Vector | Proactive | Small, stable networks |
| **DSR** | Dynamic Source Routing | Reactive | Low-overhead source routing |
| **OLSR** | Optimized Link State Routing | Proactive | Dense, large networks |

---

## Generated Outputs

Each simulation run creates a timestamped folder under `manet-platform/outputs/`:

```
outputs/<YYYY-MM-DD_HH-MM-SS>/
├── battery.csv           # Per-node energy consumption over time
├── mobility.csv          # Node positions (x, y) over time
├── throughput.csv        # PDR and throughput over time
├── flowstats.csv         # Per-flow FlowMonitor statistics
├── summary.csv           # Single-row overall summary metrics
├── manet-animation.xml   # NetAnim animation file
├── manet-*.pcap          # Wireshark-compatible packet captures
└── graphs/
    ├── battery_over_time.png
    ├── pdr_over_time.png
    ├── throughput_over_time.png
    ├── node_density.png
    ├── area_coverage.png
    ├── energy_distribution.png
    ├── flow_delay.png
    └── summary_dashboard.png
```

---

## Troubleshooting

### WSL not found / `wsl` command not recognized

- Ensure WSL2 is enabled: run `wsl --install` in PowerShell as Administrator and restart.

### `ns-3 directory not found` when running shell scripts

- NS-3 must be cloned to `~/ns-3-dev` (i.e., `/home/<your-wsl-username>/ns-3-dev`) inside WSL.
- Verify: `ls ~/ns-3-dev` in the WSL terminal.

### `ModuleNotFoundError` when launching `main.py`

- Run `pip install -r manet-platform/requirements.txt` again.
- Confirm you are using Python 3.10+: `python --version`

### NetAnim does not open

- Verify NetAnim binary exists: `ls ~/netanim/build/netanim` inside WSL.
- If missing, repeat [Part 3](#part-3--netanim-installation-inside-wsl).
- On Ubuntu 22.04, Qt5 package names differ — see the notes in Part 3.

### Build fails during `./ns3 build scratch/manet-sim`

- Check for missing dependencies: re-run the `apt install` command in Part 2.1.
- Read the full error output — it usually points to a missing library.

### Animation XML file not generated after simulation

- The simulation must complete without errors first.
- Check the Console panel (GUI) or terminal for NS-3 error messages.
- Ensure the scratch program name matches what the script calls (e.g., `lab-aodv`).

---

## Repository

**GitHub:** [https://github.com/neslang-05/manet-simulator](https://github.com/neslang-05/manet-simulator)

---

*B.Tech 8th Semester — Final Lab Project | MANET Protocol Analysis*
