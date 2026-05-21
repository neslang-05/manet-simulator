"""
analysis/comparison_engine.py — Multi-protocol comparison metric computation.
"""

from typing import Optional
from analysis.csv_parser import CSVParser


class ComparisonEngine:
    """Computes side-by-side comparison metrics for multiple experiments."""

    def __init__(self, experiments: list[dict]):
        """
        Args:
            experiments: List of dicts with 'protocol', 'output_dir' keys.
        """
        self.experiments = experiments

    def compute_comparison_table(self) -> dict:
        """
        Returns an ordered dict: metric_name -> list of values (one per experiment).
        """
        table = {
            "Protocol":              [],
            "PDR (%)":               [],
            "Avg Throughput (kbps)": [],
            "Avg Delay (ms)":        [],
            "Avg Jitter (ms)":       [],
            "Total Energy (J)":      [],
            "Dead Nodes":            [],
            "Tx Packets":            [],
            "Rx Packets":            [],
        }

        for exp in self.experiments:
            parser = CSVParser(exp.get("output_dir", ""))
            m = parser.compute_metrics()

            table["Protocol"].append(exp.get("protocol", "?"))
            table["PDR (%)"].append(
                f"{m.get('pdr', 0):.1f}" if m.get('pdr') is not None else "N/A"
            )
            table["Avg Throughput (kbps)"].append(
                f"{m.get('avgThroughput_kbps', 0):.2f}"
                if m.get('avgThroughput_kbps') is not None else "N/A"
            )
            table["Avg Delay (ms)"].append(
                f"{m.get('avgDelay_ms', 0):.2f}"
                if m.get('avgDelay_ms') is not None else "N/A"
            )
            table["Avg Jitter (ms)"].append(
                f"{m.get('avgJitter_ms', 0):.2f}"
                if m.get('avgJitter_ms') is not None else "N/A"
            )
            table["Total Energy (J)"].append(
                f"{m.get('totalEnergy', 0):.2f}"
                if m.get('totalEnergy') is not None else "N/A"
            )
            table["Dead Nodes"].append(str(m.get("deadNodes", "N/A")))
            table["Tx Packets"].append(str(m.get("txPackets", "N/A")))
            table["Rx Packets"].append(str(m.get("rxPackets", "N/A")))

        return table

    def best_protocol(self, metric: str = "PDR (%)") -> Optional[str]:
        """Return the protocol with best value for a given metric."""
        table = self.compute_comparison_table()
        protocols = table.get("Protocol", [])
        values    = table.get(metric, [])

        best_proto = None
        best_val   = None

        for proto, val_str in zip(protocols, values):
            try:
                val = float(val_str)
                if best_val is None or val > best_val:
                    best_val  = val
                    best_proto = proto
            except (ValueError, TypeError):
                continue

        return best_proto
