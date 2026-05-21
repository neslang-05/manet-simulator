"""
ui/panels/comparison.py — Protocol Comparison Panel
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
from ui.theme import COLORS, FONTS, RADIUS, PROTOCOL_COLORS
from backend.experiment_manager import ExperimentManager
from analysis.comparison_engine import ComparisonEngine
from analysis.graph_generator import ComparisonGraphGenerator
from ui.panels.graphs import GraphsPanel


class ComparisonPanel(ctk.CTkFrame):
    """Side-by-side protocol comparison panel."""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._manager  = ExperimentManager()
        self._selected = []  # list of experiment IDs
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 12))
        ctk.CTkLabel(hdr, text="⚖  Protocol Comparison",
                     font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(side="left")

        # Selection area
        sel_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                corner_radius=RADIUS["md"],
                                border_width=1, border_color=COLORS["border"])
        sel_card.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(sel_card, text="Select experiments to compare (2–4):",
                     font=FONTS["subhead"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(14, 8))

        self._exp_listbox = ctk.CTkScrollableFrame(
            sel_card, height=160, fg_color=COLORS["bg_input"],
            scrollbar_button_color=COLORS["accent_dim"]
        )
        self._exp_listbox.pack(fill="x", padx=16, pady=(0, 10))

        btn_row = ctk.CTkFrame(sel_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            btn_row, text="↻ Refresh List",
            width=130, height=32,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=6, font=FONTS["small"],
            command=self._refresh_experiments
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="⚖ Run Comparison",
            height=32,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dim"],
            text_color="#000", corner_radius=RADIUS["sm"],
            font=FONTS["subhead"],
            command=self._run_comparison
        ).pack(side="left")

        # Metrics table
        tbl_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                corner_radius=RADIUS["md"],
                                border_width=1, border_color=COLORS["border"])
        tbl_card.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(tbl_card, text="Comparison Metrics",
                     font=FONTS["subhead"], text_color=COLORS["accent"]
                     ).pack(anchor="w", padx=16, pady=(14, 8))
        self._metrics_frame = ctk.CTkFrame(tbl_card, fg_color="transparent")
        self._metrics_frame.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            self._metrics_frame,
            text="Select experiments above and click Run Comparison.",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        ).pack(pady=8)

        # Comparison graphs embedded
        self._graphs_area = ctk.CTkFrame(self, fg_color="transparent")
        self._graphs_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._refresh_experiments()

    def _refresh_experiments(self):
        for w in self._exp_listbox.winfo_children():
            w.destroy()
        self._selected = []
        self._check_vars = {}

        experiments = self._manager.get_all()
        for exp in experiments:
            var = ctk.BooleanVar(value=False)
            proto = exp.get("protocol", "?")
            color = PROTOCOL_COLORS.get(proto, COLORS["text_secondary"])
            ts    = exp.get("timestamp", "")[:19].replace("T", " ")
            label = f"{ts}  [{proto}]  Nodes:{exp.get('numNodes','?')}  ID:{exp.get('id','?')[:12]}"
            cb = ctk.CTkCheckBox(
                self._exp_listbox, text=label,
                variable=var,
                checkbox_width=16, checkbox_height=16,
                font=FONTS["small"],
                text_color=COLORS["text_primary"],
                fg_color=color,
                hover_color=COLORS["accent_dim"]
            )
            cb.pack(anchor="w", padx=8, pady=3)
            self._check_vars[exp["id"]] = (var, exp)

    def _get_selected_experiments(self) -> list:
        selected = []
        for eid, (var, exp) in self._check_vars.items():
            if var.get():
                selected.append(exp)
        return selected

    def _run_comparison(self):
        experiments = self._get_selected_experiments()
        if len(experiments) < 2:
            ctk.CTkLabel(
                self._metrics_frame,
                text="Please select at least 2 experiments.",
                text_color=COLORS["danger"], font=FONTS["small"]
            ).pack()
            return

        # Compute comparison
        engine = ComparisonEngine(
            [{"protocol": e["protocol"], "output_dir": e["output_win"]}
             for e in experiments]
        )
        table = engine.compute_comparison_table()
        self._show_metrics_table(table, experiments)

        # Generate comparison graphs
        import tempfile
        out_dir = str(Path(experiments[0]["output_win"]).parent / "comparison")
        gen = ComparisonGraphGenerator(
            [{"protocol": e["protocol"], "output_dir": e["output_win"]}
             for e in experiments],
            out_dir
        )
        paths = gen.generate_comparison()

        # Show first comparison graph
        if paths:
            for w in self._graphs_area.winfo_children():
                w.destroy()
            gp = GraphsPanel(self._graphs_area)
            gp.pack(fill="both", expand=True)
            gp.load_graphs(out_dir)

    def _show_metrics_table(self, table: dict, experiments: list):
        for w in self._metrics_frame.winfo_children():
            w.destroy()

        if not table:
            ctk.CTkLabel(self._metrics_frame,
                         text="No comparable metrics found.",
                         font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack()
            return

        grid = ctk.CTkFrame(self._metrics_frame, fg_color="transparent")
        grid.pack(fill="x")

        # Header row
        ctk.CTkLabel(grid, text="Metric", width=180,
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").grid(row=0, column=0, padx=6, pady=3)
        for i, exp in enumerate(experiments):
            proto = exp.get("protocol", "?")
            color = PROTOCOL_COLORS.get(proto, COLORS["text_secondary"])
            ctk.CTkLabel(grid, text=proto, width=120,
                         font=FONTS["subhead"],
                         text_color=color, anchor="w"
                         ).grid(row=0, column=i + 1, padx=6, pady=3)

        for r, (metric, values) in enumerate(table.items(), start=1):
            ctk.CTkLabel(grid, text=metric, width=180,
                         font=FONTS["small"],
                         text_color=COLORS["text_secondary"],
                         anchor="w").grid(row=r, column=0, padx=6, pady=2)
            for i, val in enumerate(values):
                ctk.CTkLabel(grid, text=str(val), width=120,
                             font=FONTS["small"],
                             text_color=COLORS["text_primary"],
                             anchor="w").grid(row=r, column=i + 1, padx=6, pady=2)
