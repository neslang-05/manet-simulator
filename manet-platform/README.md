# MANET Research & Visualization Platform

A professional-grade MANET (Mobile Ad-hoc Network) simulation, analysis, and visualization platform combining **NS-3**, **NetAnim**, **Python/CustomTkinter**, and **WSL2 Ubuntu**.

---

## 🏗 Architecture

```
manet-platform/
├── main.py                     # Entry point
├── requirements.txt
├── ui/                         # Python/CustomTkinter GUI
│   ├── app.py                  # Main window + navigation
│   ├── theme.py                # Design tokens
│   ├── panels/                 # 7 panel views
│   │   ├── simulation.py       # Config + run
│   │   ├── console.py          # Real-time log
│   │   ├── results.py          # Metric dashboard
│   │   ├── graphs.py           # Graph viewer
│   │   ├── history.py          # Experiment history
│   │   ├── comparison.py       # Protocol comparison
│   │   └── diagnostics.py      # WSL diagnostics
│   └── widgets/
│       └── stat_card.py        # Metric card widget
├── backend/
│   ├── wsl_bridge.py           # WSL subprocess bridge
│   ├── sim_runner.py           # Simulation orchestrator
│   ├── experiment_manager.py   # History management
│   └── logger.py
├── ns3/
│   ├── manet-sim.cc            # Unified NS-3 simulation
│   └── install.sh              # Build helper
├── analysis/
│   ├── csv_parser.py           # Output file parsing
│   ├── graph_generator.py      # Matplotlib graph generation
│   ├── comparison_engine.py    # Multi-protocol comparison
│   └── metrics_calculator.py
├── configs/
│   ├── defaults.json           # Default parameters
│   └── presets.json            # Named presets
└── outputs/                    # Simulation outputs (auto-created)
```

---

## ⚡ Quick Start

### 1. Install Python dependencies

```bash
pip install customtkinter matplotlib pandas numpy Pillow
```

### 2. First-time setup: Install NS-3 simulation file

Open the platform, navigate to **Diagnostics**, and click **"Install & Build manet-sim"**.

This copies `ns3/manet-sim.cc` into `~/ns-3-dev/scratch/` and builds it.

### 3. Launch the platform

```bash
python main.py
```

---

## 🖥 Environment Requirements

| Component | Location |
|-----------|----------|
| OS | Windows 11 |
| Python | Windows (≥3.10) |
| WSL2 | Ubuntu |
| NS-3 | `~/ns-3-dev` (in WSL) |
| NetAnim | `~/netanim/build/netanim` (in WSL) |

---

## 🔬 Supported Protocols

| Protocol | Description |
|----------|-------------|
| **AODV** | Ad-hoc On-demand Distance Vector |
| **DSDV** | Destination-Sequenced Distance Vector |
| **DSR**  | Dynamic Source Routing |
| **OLSR** | Optimized Link State Routing |

---

## 🛠 Simulation Parameters

| Parameter | Range | Default |
|-----------|-------|---------|
| Number of Nodes | 5–100 | 20 |
| Simulation Time | 10–600 s | 60 s |
| Area Width/Height | 200–5000 m | 1000 m |
| Node Speed | 1–50 m/s | 10 m/s |
| Pause Time | 0–30 s | 2 s |
| Battery Capacity | 10–500 J | 100 J |
| TX Range | 50–1000 m | 250 m |
| Packet Size | 64–4096 bytes | 512 bytes |
| Data Rate | 512K–10Mbps | 2Mbps |

---

## 📊 Generated Outputs

Each simulation run creates a timestamped folder with:

```
outputs/<timestamp>/
├── battery.csv         # Per-node energy over time
├── mobility.csv        # Node positions over time
├── throughput.csv      # PDR + throughput over time
├── flowstats.csv       # Per-flow FlowMonitor stats
├── summary.csv         # Single-row overall summary
├── manet-animation.xml # NetAnim animation file
├── manet-*.pcap        # PCAP traces
└── graphs/             # Auto-generated PNG graphs
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

## 🚀 Built-in Presets

- **Small Network** — 10 nodes, 500×500 m, AODV
- **Medium Network** — 30 nodes, 1500×1500 m, OLSR
- **Large Network** — 50 nodes, 2000×2000 m, DSDV
- **Energy Stress Test** — 40 nodes, low battery, AODV
- **High Mobility** — 25 nodes, 30 m/s, DSR

---

## 🔌 WSL Integration

All NS-3 commands run via WSL:

```python
wsl bash -c 'cd ~/ns-3-dev && ./ns3 run "scratch/manet-sim --protocol=AODV ..."'
```

Path translation: Windows paths ↔ WSL `/mnt/...` paths is handled automatically.

---

## 📈 Scalability

The platform is designed to support future extensions:

- VANET (Vehicular Networks)
- WSN (Wireless Sensor Networks)
- IoT network simulation
- SDN-enabled MANET
- UAV network topologies
- AI-based adaptive routing protocols

---

## 👨‍🔬 Research Workflow

1. **Configure** parameters in the Simulation panel
2. **Run** the simulation (NS-3 executes in WSL)
3. **Monitor** real-time logs in the Console panel
4. **Review** metrics in the Results dashboard
5. **Explore** graphs in the Graph Viewer
6. **Compare** multiple protocol experiments side-by-side
7. **Export** CSVs and PNGs for publications
8. **Re-run** any past experiment from History
