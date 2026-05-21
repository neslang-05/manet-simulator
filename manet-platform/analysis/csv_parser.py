"""
csv_parser.py — Parse all CSV output files produced by NS-3 simulation.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional


class CSVParser:
    """Parses NS-3 simulation CSV output files."""

    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Windows path to the experiment output folder.
        """
        self.output_dir = Path(output_dir)

    def _load(self, filename: str) -> Optional[pd.DataFrame]:
        """Load a CSV file, return DataFrame or None if missing/empty."""
        path = self.output_dir / filename
        if not path.exists():
            return None
        try:
            df = pd.read_csv(path)
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"[CSVParser] Error loading {filename}: {e}")
            return None

    def get_battery(self) -> Optional[pd.DataFrame]:
        """Load battery.csv — columns: Time, NodeID, RemainingEnergy."""
        return self._load("battery.csv")

    def get_mobility(self) -> Optional[pd.DataFrame]:
        """Load mobility.csv — columns: Time, NodeID, X, Y."""
        return self._load("mobility.csv")

    def get_throughput(self) -> Optional[pd.DataFrame]:
        """Load throughput.csv — columns: Time, TxPackets, RxPackets, PDR, Throughput_kbps."""
        return self._load("throughput.csv")

    def get_flowstats(self) -> Optional[pd.DataFrame]:
        """Load flowstats.csv — per-flow statistics from FlowMonitor."""
        return self._load("flowstats.csv")

    def get_summary(self) -> Optional[pd.DataFrame]:
        """Load summary.csv — single-row overall summary."""
        return self._load("summary.csv")

    def get_summary_dict(self) -> dict:
        """Return summary as a dictionary, with safe defaults."""
        df = self.get_summary()
        if df is None or df.empty:
            return {}
        return df.iloc[0].to_dict()

    def compute_metrics(self) -> dict:
        """Compute derived metrics from all CSV data."""
        metrics = {}

        # Summary metrics
        summary = self.get_summary_dict()
        if summary:
            metrics["protocol"]    = summary.get("Protocol", "N/A")
            metrics["numNodes"]    = int(summary.get("NumNodes", 0))
            metrics["simTime"]     = float(summary.get("SimTime", 0))
            metrics["txPackets"]   = int(summary.get("TxPackets", 0))
            metrics["rxPackets"]   = int(summary.get("RxPackets", 0))
            metrics["pdr"]         = float(summary.get("PDR", 0))
            metrics["totalEnergy"] = float(summary.get("TotalEnergyRemaining", 0))
            metrics["deadNodes"]   = int(summary.get("DeadNodes", 0))

        # Flow stats averages
        flows = self.get_flowstats()
        if flows is not None and not flows.empty:
            metrics["avgThroughput_kbps"] = flows["Throughput_kbps"].mean()
            metrics["avgDelay_ms"]        = flows["MeanDelay_ms"].mean()
            metrics["avgJitter_ms"]       = flows["MeanJitter_ms"].mean()
            metrics["totalFlows"]         = len(flows)

        # Battery stats
        battery = self.get_battery()
        if battery is not None and not battery.empty:
            last_time = battery["Time"].max()
            last = battery[battery["Time"] == last_time]
            metrics["avgRemainingEnergy"] = last["RemainingEnergy"].mean()
            metrics["minRemainingEnergy"] = last["RemainingEnergy"].min()
            metrics["maxRemainingEnergy"] = last["RemainingEnergy"].max()
            dead = (last["RemainingEnergy"] < 0.001).sum()
            metrics["deadNodesFromBattery"] = int(dead)

        # Mobility stats
        mob = self.get_mobility()
        if mob is not None and not mob.empty:
            metrics["areaUtilization"] = self._compute_coverage(mob)

        return metrics

    def _compute_coverage(self, mobility_df: pd.DataFrame) -> float:
        """Estimate area coverage as fraction of 100x100 grid cells visited."""
        try:
            x_max = mobility_df["X"].max()
            y_max = mobility_df["Y"].max()
            if x_max == 0 or y_max == 0:
                return 0.0
            grid_size = 10
            x_bins = pd.cut(mobility_df["X"], bins=grid_size)
            y_bins = pd.cut(mobility_df["Y"], bins=grid_size)
            cells = mobility_df.groupby([x_bins, y_bins]).size()
            visited = (cells > 0).sum()
            total = grid_size * grid_size
            return round(100.0 * visited / total, 1)
        except Exception:
            return 0.0
