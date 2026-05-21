"""
graph_generator.py — Automated graph generation from NS-3 simulation data.
Produces publication-quality Matplotlib figures.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for file saving
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
from pathlib import Path
from typing import Optional

from analysis.csv_parser import CSVParser

# ── Color palette ──────────────────────────────────────────────────────────
PROTOCOL_COLORS = {
    "AODV": "#004085",
    "DSDV": "#C82333",
    "DSR":  "#218838",
    "OLSR": "#D39E00",
}

STYLE = {
    "bg":      "#F5F7FA",
    "fg":      "#212529",
    "grid":    "#DEE2E6",
    "accent":  "#003366",
    "spine":   "#DEE2E6",
}


def _apply_dark_style(ax, title: str, xlabel: str, ylabel: str):
    """Apply consistent dark theme to an axis."""
    fig = ax.get_figure()
    fig.patch.set_facecolor(STYLE["bg"])
    ax.set_facecolor(STYLE["bg"])
    ax.set_title(title, color=STYLE["fg"], fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, color=STYLE["fg"], fontsize=10)
    ax.set_ylabel(ylabel, color=STYLE["fg"], fontsize=10)
    ax.tick_params(colors=STYLE["fg"])
    ax.grid(True, color=STYLE["grid"], linewidth=0.6, linestyle='--', alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor(STYLE["spine"])
    return ax


def _save(fig, path: str):
    """Save figure to PNG with tight layout."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=STYLE["bg"], edgecolor='none')
    plt.close(fig)


class GraphGenerator:
    """Generates all required analysis graphs for a simulation run."""

    def __init__(self, output_dir: str, protocol: str = "AODV"):
        self.output_dir = Path(output_dir)
        self.graphs_dir = self.output_dir / "graphs"
        self.graphs_dir.mkdir(parents=True, exist_ok=True)
        self.protocol = protocol
        self.color = PROTOCOL_COLORS.get(protocol, "#00C6FF")
        self.parser = CSVParser(str(output_dir))

    def generate_all(self) -> list[str]:
        """Generate all graphs, return list of saved PNG paths."""
        generated = []
        generators = [
            self.graph_battery_over_time,
            self.graph_pdr_over_time,
            self.graph_throughput_over_time,
            self.graph_node_density,
            self.graph_area_coverage,
            self.graph_energy_distribution,
            self.graph_flow_delay,
            self.graph_summary_dashboard,
        ]
        for fn in generators:
            try:
                path = fn()
                if path:
                    generated.append(path)
            except Exception as e:
                print(f"[GraphGen] Error in {fn.__name__}: {e}")
        return generated

    # ── 1. Battery over time ────────────────────────────────────────────────
    def graph_battery_over_time(self) -> Optional[str]:
        df = self.parser.get_battery()
        if df is None:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        _apply_dark_style(ax,
            f"Battery Consumption Over Time ({self.protocol})",
            "Time (s)", "Remaining Energy (J)")

        # Average across all nodes
        avg = df.groupby("Time")["RemainingEnergy"].mean()
        mn  = df.groupby("Time")["RemainingEnergy"].min()
        mx  = df.groupby("Time")["RemainingEnergy"].max()

        ax.plot(avg.index, avg.values, color=self.color, linewidth=2,
                label="Average Energy")
        ax.fill_between(avg.index, mn.values, mx.values,
                        alpha=0.2, color=self.color, label="Min–Max Range")
        ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["fg"])

        path = str(self.graphs_dir / "battery_over_time.png")
        _save(fig, path)
        return path

    # ── 2. PDR over time ────────────────────────────────────────────────────
    def graph_pdr_over_time(self) -> Optional[str]:
        df = self.parser.get_throughput()
        if df is None:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        _apply_dark_style(ax,
            f"Packet Delivery Ratio Over Time ({self.protocol})",
            "Time (s)", "PDR (%)")

        ax.plot(df["Time"], df["PDR"], color=self.color, linewidth=2)
        ax.set_ylim(0, 105)
        ax.axhline(y=df["PDR"].mean(), color="#FF6B6B", linestyle='--',
                   linewidth=1.2, label=f"Mean: {df['PDR'].mean():.1f}%")
        ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["fg"])

        path = str(self.graphs_dir / "pdr_over_time.png")
        _save(fig, path)
        return path

    # ── 3. Throughput over time ─────────────────────────────────────────────
    def graph_throughput_over_time(self) -> Optional[str]:
        df = self.parser.get_throughput()
        if df is None:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        _apply_dark_style(ax,
            f"Network Throughput Over Time ({self.protocol})",
            "Time (s)", "Throughput (kbps)")

        ax.fill_between(df["Time"], df["Throughput_kbps"],
                        alpha=0.3, color=self.color)
        ax.plot(df["Time"], df["Throughput_kbps"],
                color=self.color, linewidth=2)

        path = str(self.graphs_dir / "throughput_over_time.png")
        _save(fig, path)
        return path

    # ── 4. Node density (mobility heatmap) ─────────────────────────────────
    def graph_node_density(self) -> Optional[str]:
        df = self.parser.get_mobility()
        if df is None:
            return None

        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor(STYLE["bg"])
        ax.set_facecolor(STYLE["bg"])
        ax.set_title(f"Node Density Heatmap ({self.protocol})",
                     color=STYLE["fg"], fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("X Position (m)", color=STYLE["fg"])
        ax.set_ylabel("Y Position (m)", color=STYLE["fg"])
        ax.tick_params(colors=STYLE["fg"])

        h = ax.hist2d(df["X"], df["Y"], bins=20, cmap="plasma")
        cbar = fig.colorbar(h[3], ax=ax)
        cbar.set_label("Visit Count", color=STYLE["fg"])
        cbar.ax.yaxis.set_tick_params(color=STYLE["fg"])
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color=STYLE["fg"])

        path = str(self.graphs_dir / "node_density.png")
        _save(fig, path)
        return path

    # ── 5. Area coverage over time ──────────────────────────────────────────
    def graph_area_coverage(self) -> Optional[str]:
        df = self.parser.get_mobility()
        if df is None:
            return None

        times = sorted(df["Time"].unique())
        coverage = []
        for t in times:
            snapshot = df[df["Time"] <= t]
            x_bins = pd.cut(snapshot["X"], bins=10, labels=False)
            y_bins = pd.cut(snapshot["Y"], bins=10, labels=False)
            cells  = snapshot.groupby([x_bins, y_bins]).size()
            visited = (cells > 0).sum()
            coverage.append(100.0 * visited / 100)

        fig, ax = plt.subplots(figsize=(10, 5))
        _apply_dark_style(ax,
            f"Area Coverage Over Time ({self.protocol})",
            "Time (s)", "Coverage (%)")
        ax.plot(times, coverage, color=self.color, linewidth=2)
        ax.set_ylim(0, 105)
        ax.fill_between(times, coverage, alpha=0.15, color=self.color)

        path = str(self.graphs_dir / "area_coverage.png")
        _save(fig, path)
        return path

    # ── 6. Energy distribution at end ──────────────────────────────────────
    def graph_energy_distribution(self) -> Optional[str]:
        df = self.parser.get_battery()
        if df is None:
            return None

        last_time = df["Time"].max()
        last = df[df["Time"] == last_time]

        fig, ax = plt.subplots(figsize=(9, 5))
        _apply_dark_style(ax,
            f"Final Energy Distribution ({self.protocol})",
            "Node ID", "Remaining Energy (J)")

        colors = [
            "#FF4444" if e < 10 else "#FFD43B" if e < 50 else self.color
            for e in last["RemainingEnergy"].values
        ]
        ax.bar(last["NodeID"], last["RemainingEnergy"], color=colors, width=0.8)

        path = str(self.graphs_dir / "energy_distribution.png")
        _save(fig, path)
        return path

    # ── 7. Flow delay distribution ──────────────────────────────────────────
    def graph_flow_delay(self) -> Optional[str]:
        df = self.parser.get_flowstats()
        if df is None:
            return None
        df = df[df["MeanDelay_ms"] > 0]
        if df.empty:
            return None

        fig, ax = plt.subplots(figsize=(9, 5))
        _apply_dark_style(ax,
            f"End-to-End Delay Distribution ({self.protocol})",
            "Delay (ms)", "Number of Flows")

        ax.hist(df["MeanDelay_ms"], bins=20, color=self.color, edgecolor=STYLE["bg"])
        ax.axvline(df["MeanDelay_ms"].mean(), color="#FF6B6B", linestyle='--',
                   linewidth=1.5, label=f"Mean: {df['MeanDelay_ms'].mean():.1f} ms")
        ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["fg"])

        path = str(self.graphs_dir / "flow_delay.png")
        _save(fig, path)
        return path

    # ── 8. Summary dashboard (4-panel) ─────────────────────────────────────
    def graph_summary_dashboard(self) -> Optional[str]:
        tp_df   = self.parser.get_throughput()
        bat_df  = self.parser.get_battery()
        flow_df = self.parser.get_flowstats()
        if tp_df is None and bat_df is None:
            return None

        fig = plt.figure(figsize=(14, 8))
        fig.patch.set_facecolor(STYLE["bg"])
        gs = GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

        # Panel 1: PDR
        if tp_df is not None:
            ax1 = fig.add_subplot(gs[0, 0])
            _apply_dark_style(ax1, "PDR Over Time", "Time (s)", "PDR (%)")
            ax1.plot(tp_df["Time"], tp_df["PDR"], color=self.color, lw=2)
            ax1.set_ylim(0, 105)

        # Panel 2: Throughput
        if tp_df is not None:
            ax2 = fig.add_subplot(gs[0, 1])
            _apply_dark_style(ax2, "Throughput", "Time (s)", "kbps")
            ax2.fill_between(tp_df["Time"], tp_df["Throughput_kbps"],
                             alpha=0.25, color=self.color)
            ax2.plot(tp_df["Time"], tp_df["Throughput_kbps"], color=self.color, lw=2)

        # Panel 3: Battery
        if bat_df is not None:
            ax3 = fig.add_subplot(gs[1, 0])
            _apply_dark_style(ax3, "Average Battery", "Time (s)", "Energy (J)")
            avg = bat_df.groupby("Time")["RemainingEnergy"].mean()
            ax3.plot(avg.index, avg.values, color="#FFD43B", lw=2)

        # Panel 4: Delay histogram
        if flow_df is not None and not flow_df.empty:
            filt = flow_df[flow_df["MeanDelay_ms"] > 0]
            if not filt.empty:
                ax4 = fig.add_subplot(gs[1, 1])
                _apply_dark_style(ax4, "Delay Distribution", "Delay (ms)", "Flows")
                ax4.hist(filt["MeanDelay_ms"], bins=15, color="#51CF66",
                         edgecolor=STYLE["bg"])

        fig.suptitle(f"Simulation Summary Dashboard — {self.protocol}",
                     color=STYLE["fg"], fontsize=15, fontweight='bold', y=1.01)

        path = str(self.graphs_dir / "summary_dashboard.png")
        _save(fig, path)
        return path


class ComparisonGraphGenerator:
    """Generates side-by-side comparison graphs for multiple experiments."""

    def __init__(self, experiments: list[dict], output_dir: str):
        """
        Args:
            experiments: List of dicts with 'protocol', 'output_dir' keys.
            output_dir: Where to save comparison graphs.
        """
        self.experiments = experiments
        self.output_dir  = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_comparison(self) -> list[str]:
        """Generate protocol comparison graphs."""
        generated = []
        try:
            path = self._compare_pdr()
            if path:
                generated.append(path)
        except Exception as e:
            print(f"[CompGraph] PDR compare error: {e}")
        try:
            path = self._compare_battery()
            if path:
                generated.append(path)
        except Exception as e:
            print(f"[CompGraph] Battery compare error: {e}")
        try:
            path = self._compare_throughput()
            if path:
                generated.append(path)
        except Exception as e:
            print(f"[CompGraph] Throughput compare error: {e}")
        return generated

    def _compare_pdr(self) -> Optional[str]:
        fig, ax = plt.subplots(figsize=(11, 6))
        _apply_dark_style(ax, "PDR Comparison Across Protocols",
                          "Time (s)", "PDR (%)")
        for exp in self.experiments:
            parser = CSVParser(exp["output_dir"])
            df = parser.get_throughput()
            if df is not None:
                proto = exp["protocol"]
                color = PROTOCOL_COLORS.get(proto, "#FFFFFF")
                ax.plot(df["Time"], df["PDR"], color=color,
                        linewidth=2, label=proto)
        ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["fg"])
        path = str(self.output_dir / "compare_pdr.png")
        _save(fig, path)
        return path

    def _compare_battery(self) -> Optional[str]:
        fig, ax = plt.subplots(figsize=(11, 6))
        _apply_dark_style(ax, "Average Battery Consumption Comparison",
                          "Time (s)", "Avg Energy (J)")
        for exp in self.experiments:
            parser = CSVParser(exp["output_dir"])
            df = parser.get_battery()
            if df is not None:
                avg   = df.groupby("Time")["RemainingEnergy"].mean()
                proto = exp["protocol"]
                color = PROTOCOL_COLORS.get(proto, "#FFFFFF")
                ax.plot(avg.index, avg.values, color=color,
                        linewidth=2, label=proto)
        ax.legend(facecolor=STYLE["bg"], labelcolor=STYLE["fg"])
        path = str(self.output_dir / "compare_battery.png")
        _save(fig, path)
        return path

    def _compare_throughput(self) -> Optional[str]:
        protocols, avg_tp = [], []
        for exp in self.experiments:
            parser = CSVParser(exp["output_dir"])
            df = parser.get_throughput()
            if df is not None:
                avg_tp.append(df["Throughput_kbps"].mean())
                protocols.append(exp["protocol"])
        if not protocols:
            return None

        fig, ax = plt.subplots(figsize=(9, 6))
        _apply_dark_style(ax, "Average Throughput Comparison",
                          "Protocol", "Avg Throughput (kbps)")
        colors = [PROTOCOL_COLORS.get(p, "#FFFFFF") for p in protocols]
        bars = ax.bar(protocols, avg_tp, color=colors, width=0.5)
        for bar, val in zip(bars, avg_tp):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{val:.1f}", ha='center', color=STYLE["fg"], fontsize=10)

        path = str(self.output_dir / "compare_throughput.png")
        _save(fig, path)
        return path
