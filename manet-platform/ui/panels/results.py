"""
ui/panels/results.py — Results Dashboard Panel
Displays simulation metrics, summary cards, and tables.
"""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from ui.theme import COLORS, FONTS, RADIUS, PROTOCOL_COLORS
from ui.widgets.stat_card import StatCard
from analysis.csv_parser import CSVParser


class ResultsPanel(ctk.CTkScrollableFrame):
    """Results dashboard with metric cards and tables."""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        kwargs.setdefault("scrollbar_fg_color", COLORS["bg_primary"])
        kwargs.setdefault("scrollbar_button_color", COLORS["accent_dim"])
        super().__init__(parent, **kwargs)
        self._current_dir = None
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 8))
        ctk.CTkLabel(hdr, text="📊  Results Dashboard",
                     font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(side="left")

        self._export_btn = ctk.CTkButton(
            hdr, text="⬇ Export CSV",
            width=130, height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            border_width=1, border_color=COLORS["accent"],
            corner_radius=6, font=FONTS["small"],
            command=self._export
        )
        self._export_btn.pack(side="right")

        self._proto_lbl = ctk.CTkLabel(
            hdr, text="No results loaded",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        self._proto_lbl.pack(side="right", padx=12)

        # Metric cards grid (2x4)
        self._cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._cards_frame.pack(fill="x", padx=20, pady=(0, 14))
        for i in range(4):
            self._cards_frame.columnconfigure(i, weight=1)

        card_defs = [
            ("pdr",           "Packet Delivery Ratio", "--", "%",    COLORS["accent"]),
            ("throughput",    "Avg Throughput",         "--", "kbps", COLORS["success"]),
            ("delay",         "Avg E2E Delay",          "--", "ms",   COLORS["warning"]),
            ("txPackets",     "Packets Sent",           "--", "",     COLORS["purple"]),
            ("rxPackets",     "Packets Received",       "--", "",     COLORS["proto_aodv"]),
            ("totalEnergy",   "Energy Remaining",       "--", "J",    COLORS["proto_dsr"]),
            ("deadNodes",     "Dead Nodes",             "--", "",     COLORS["danger"]),
            ("simTime",       "Simulation Time",        "--", "s",    COLORS["text_secondary"]),
        ]
        self._stat_cards = {}
        for idx, (key, title, val, unit, accent) in enumerate(card_defs):
            r, c = divmod(idx, 4)
            card = StatCard(self._cards_frame, title=title, value=val,
                            unit=unit, accent=accent)
            card.grid(row=r, column=c, padx=6, pady=6, sticky="ew")
            self._stat_cards[key] = card

        # Flow stats table
        tbl_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                corner_radius=RADIUS["md"],
                                border_width=1, border_color=COLORS["border"])
        tbl_card.pack(fill="both", padx=20, pady=(0, 20), expand=True)
        ctk.CTkLabel(tbl_card, text="Flow Statistics",
                     font=FONTS["subhead"], text_color=COLORS["accent"]
                     ).pack(anchor="w", padx=16, pady=(14, 8))

        # Table
        self._table_frame = ctk.CTkFrame(tbl_card, fg_color="transparent")
        self._table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self._build_table_header()

    def _build_table_header(self):
        cols = ["Flow ID", "Src Port", "Dst Port", "Tx Pkts",
                "Rx Pkts", "Throughput (kbps)", "Delay (ms)", "Jitter (ms)"]
        widths = [70, 80, 80, 80, 80, 160, 100, 100]
        for i, (col, w) in enumerate(zip(cols, widths)):
            lbl = ctk.CTkLabel(
                self._table_frame, text=col, width=w,
                font=FONTS["small"], text_color=COLORS["text_muted"],
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=4, pady=4, sticky="w")

        sep = ctk.CTkFrame(self._table_frame, height=1,
                           fg_color=COLORS["border"])
        sep.grid(row=1, column=0, columnspan=len(cols), sticky="ew", pady=2)
        self._table_start_row = 2

    def load_results(self, output_dir: str, protocol: str = "N/A"):
        """Load and display results from an experiment output directory."""
        self._current_dir = output_dir
        self._proto_lbl.configure(
            text=f"Protocol: {protocol}  |  {output_dir[:50]}..."
            if len(output_dir) > 50 else f"Protocol: {protocol}  |  {output_dir}"
        )

        try:
            parser = CSVParser(output_dir)
            metrics = parser.compute_metrics()
            self._update_cards(metrics)
            self._update_table(parser)
        except Exception as e:
            print(f"[ResultsPanel] Load error: {e}")

    def _update_cards(self, m: dict):
        def fmt(v, dec=1):
            if v is None:
                return "--"
            try:
                return f"{float(v):.{dec}f}"
            except Exception:
                return str(v)

        self._stat_cards["pdr"].update_value(fmt(m.get("pdr")))
        self._stat_cards["throughput"].update_value(fmt(m.get("avgThroughput_kbps")))
        self._stat_cards["delay"].update_value(fmt(m.get("avgDelay_ms")))
        self._stat_cards["txPackets"].update_value(str(m.get("txPackets", "--")))
        self._stat_cards["rxPackets"].update_value(str(m.get("rxPackets", "--")))
        self._stat_cards["totalEnergy"].update_value(fmt(m.get("totalEnergy")))
        self._stat_cards["deadNodes"].update_value(str(m.get("deadNodes", "--")))
        self._stat_cards["simTime"].update_value(fmt(m.get("simTime"), 0))

        # Color dead nodes red if > 0
        dead = m.get("deadNodes", 0)
        if dead and int(dead) > 0:
            self._stat_cards["deadNodes"].set_accent(COLORS["danger"])
        else:
            self._stat_cards["deadNodes"].set_accent(COLORS["success"])

    def _update_table(self, parser: CSVParser):
        # Clear old rows
        for widget in self._table_frame.grid_slaves():
            r = int(widget.grid_info().get("row", 0))
            if r >= self._table_start_row:
                widget.destroy()

        df = parser.get_flowstats()
        if df is None or df.empty:
            ctk.CTkLabel(
                self._table_frame, text="No flow data available.",
                font=FONTS["small"], text_color=COLORS["text_muted"]
            ).grid(row=self._table_start_row, column=0, columnspan=8,
                   padx=4, pady=8, sticky="w")
            return

        for i, (_, row) in enumerate(df.iterrows()):
            bg = COLORS["bg_primary"] if i % 2 == 0 else COLORS["bg_card"]
            vals = [
                str(int(row.get("FlowID", ""))),
                str(int(row.get("SrcPort", ""))),
                str(int(row.get("DstPort", ""))),
                str(int(row.get("TxPackets", 0))),
                str(int(row.get("RxPackets", 0))),
                f"{float(row.get('Throughput_kbps', 0)):.2f}",
                f"{float(row.get('MeanDelay_ms', 0)):.2f}",
                f"{float(row.get('MeanJitter_ms', 0)):.2f}",
            ]
            for j, val in enumerate(vals):
                ctk.CTkLabel(
                    self._table_frame, text=val,
                    font=FONTS["small"],
                    text_color=COLORS["text_primary"],
                    anchor="w"
                ).grid(row=self._table_start_row + i, column=j,
                       padx=4, pady=2, sticky="w")

    def _export(self):
        if not self._current_dir:
            return
        from tkinter import filedialog
        import shutil
        dest = filedialog.askdirectory(title="Select export destination")
        if dest:
            for f in Path(self._current_dir).glob("*.csv"):
                shutil.copy(f, dest)
