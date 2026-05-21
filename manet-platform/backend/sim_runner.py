"""
sim_runner.py — Simulation Orchestrator
Manages the full lifecycle: build -> run -> collect -> analyze
"""

import os
import json
import time
import datetime
from dataclasses import dataclass, asdict
from typing import Callable, Optional
from pathlib import Path

from backend.wsl_bridge import WSLBridge


@dataclass
class SimConfig:
    """All simulation parameters."""
    protocol:      str   = "AODV"
    numNodes:      int   = 20
    simTime:       float = 60.0
    areaWidth:     float = 1000.0
    areaHeight:    float = 1000.0
    speed:         float = 10.0
    pauseTime:     float = 2.0
    battery:       float = 100.0
    txRange:       float = 250.0
    packetSize:    int   = 512
    dataRate:      str   = "2Mbps"
    mobilityModel: str   = "RandomWaypoint"


class SimRunner:
    """Orchestrates a complete simulation run."""

    BASE_OUTPUT_WSL   = "~/ns-3-dev/manet_outputs"
    BASE_OUTPUT_DIRS  = ["csv", "graphs", "logs", "pcap", "xml"]

    def __init__(self):
        self.bridge   = WSLBridge()
        self.config   = SimConfig()
        self.run_id:  Optional[str] = None
        self.is_running = False
        self._log_cb: Optional[Callable[[str], None]] = None
        self._done_cb: Optional[Callable[[bool, dict], None]] = None

    def set_config(self, config: SimConfig):
        self.config = config

    def _log(self, msg: str):
        if self._log_cb:
            self._log_cb(msg)

    def run(
        self,
        on_log: Callable[[str], None],
        on_done: Callable[[bool, dict], None]
    ):
        """Start the simulation. Calls on_done(success, result_dict) when finished."""
        self._log_cb  = on_log
        self._done_cb = on_done
        self.is_running = True

        # Create timestamp-based run ID
        self.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        username = self.bridge.get_wsl_username()
        base_output = self.BASE_OUTPUT_WSL.replace("~", f"/home/{username}")
        output_dir_wsl = f"{base_output}/{self.run_id}"

        self._log(f"[Runner] Starting simulation run: {self.run_id}")
        self._log(f"[Runner] Protocol: {self.config.protocol}, Nodes: {self.config.numNodes}")
        self._log(f"[Runner] Output dir: {output_dir_wsl}")

        params = asdict(self.config)
        params.pop('mobilityModel', None)  # handled in C++

        self.bridge.run_simulation(
            params=params,
            output_dir_wsl=output_dir_wsl,
            on_output=self._handle_output,
            on_done=lambda rc: self._handle_done(rc, output_dir_wsl)
        )

    def _handle_output(self, line: str):
        self._log(line)

    def _handle_done(self, returncode: int, output_dir_wsl: str):
        self.is_running = False
        success = (returncode == 0)

        if success:
            self._log("[Runner] Simulation completed successfully.")
        else:
            self._log(f"[Runner] Simulation failed with code {returncode}.")

        # Translate WSL output dir to Windows path
        windows_path = self.bridge.wsl_path_to_windows(output_dir_wsl)

        result = {
            "run_id":       self.run_id,
            "success":      success,
            "returncode":   returncode,
            "config":       asdict(self.config),
            "output_wsl":   output_dir_wsl,
            "output_win":   windows_path,
            "timestamp":    self.run_id,
        }

        if self._done_cb:
            self._done_cb(success, result)

    def cancel(self):
        """Cancel the running simulation."""
        if self.is_running:
            self._log("[Runner] Cancelling simulation...")
            self.bridge.cancel()
