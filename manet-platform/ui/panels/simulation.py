"""
ui/panels/simulation.py — Simulation Configuration Panel
Allows users to configure all MANET simulation parameters.
"""

import customtkinter as ctk
import json
from pathlib import Path
from tkinter import messagebox
from typing import Callable, Optional

from ui.theme import COLORS, FONTS, SPACING, RADIUS, PROTOCOL_COLORS
from backend.sim_runner import SimConfig


class SimulationPanel(ctk.CTkScrollableFrame):
    """Complete simulation configuration and launch panel."""

    PROTOCOLS       = ["AODV", "DSDV", "DSR", "OLSR"]
    MOBILITY_MODELS = ["RandomWaypoint", "RandomWalk", "GaussMarkov"]
    DATA_RATES      = ["512Kbps", "1Mbps", "2Mbps", "5Mbps", "10Mbps"]

    def __init__(self, parent, on_run: Callable, on_cancel: Callable,
                 on_install: Callable, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        kwargs.setdefault("scrollbar_fg_color", COLORS["bg_primary"])
        kwargs.setdefault("scrollbar_button_color", COLORS["accent_dim"])
        super().__init__(parent, **kwargs)

        self._on_run     = on_run
        self._on_cancel  = on_cancel
        self._on_install = on_install
        self._is_running = False

        self._presets = self._load_presets()
        self._vars    = {}

        self._build_ui()

    def _load_presets(self) -> dict:
        try:
            p = Path(__file__).parent.parent.parent / "configs" / "presets.json"
            with open(p) as f:
                return json.load(f)
        except Exception:
            return {}

    # ── Build UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 8))
        ctk.CTkLabel(hdr, text="⚙  Simulation Configuration",
                     font=FONTS["heading"], text_color=COLORS["text_primary"]).pack(side="left")

        # Presets row
        self._build_presets_row()

        # Parameters grid
        params_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                   corner_radius=RADIUS["md"],
                                   border_width=1, border_color=COLORS["border"])
        params_card.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(params_card, text="Network Parameters",
                     font=FONTS["subhead"], text_color=COLORS["accent"]
                     ).pack(anchor="w", padx=16, pady=(14, 4))

        grid = ctk.CTkFrame(params_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 14))
        grid.columnconfigure((0, 1), weight=1, uniform="col")

        # Row 0
        self._param_slider(grid, 0, 0, "Number of Nodes", "numNodes",
                           5, 100, 20, int)
        self._param_slider(grid, 0, 1, "Simulation Time (s)", "simTime",
                           10, 600, 60, float)
        # Row 1
        self._param_slider(grid, 1, 0, "Area Width (m)", "areaWidth",
                           200, 5000, 1000, float)
        self._param_slider(grid, 1, 1, "Area Height (m)", "areaHeight",
                           200, 5000, 1000, float)
        # Row 2
        self._param_slider(grid, 2, 0, "Node Speed (m/s)", "speed",
                           1, 50, 10, float)
        self._param_slider(grid, 2, 1, "Pause Time (s)", "pauseTime",
                           0, 30, 2, float)
        # Row 3
        self._param_slider(grid, 3, 0, "Battery Capacity (J)", "battery",
                           10, 500, 100, float)
        self._param_slider(grid, 3, 1, "TX Range (m)", "txRange",
                           50, 1000, 250, float)
        # Row 4
        self._param_slider(grid, 4, 0, "Packet Size (bytes)", "packetSize",
                           64, 4096, 512, int)

        # Protocol + mobility dropdowns
        proto_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                  corner_radius=RADIUS["md"],
                                  border_width=1, border_color=COLORS["border"])
        proto_card.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(proto_card, text="Protocol & Mobility",
                     font=FONTS["subhead"], text_color=COLORS["accent"]
                     ).pack(anchor="w", padx=16, pady=(14, 8))

        drop_row = ctk.CTkFrame(proto_card, fg_color="transparent")
        drop_row.pack(fill="x", padx=16, pady=(0, 14))
        drop_row.columnconfigure((0, 1, 2), weight=1)

        # Protocol
        self._param_dropdown(drop_row, 0, "Routing Protocol", "protocol",
                             self.PROTOCOLS, "AODV")
        # Mobility
        self._param_dropdown(drop_row, 1, "Mobility Model", "mobilityModel",
                             self.MOBILITY_MODELS, "RandomWaypoint")
        # Data rate
        self._param_dropdown(drop_row, 2, "Data Rate", "dataRate",
                             self.DATA_RATES, "2Mbps")

        # Action buttons
        self._build_action_buttons()

    def _build_presets_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(row, text="Presets:",
                     font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 8))

        for name in self._presets:
            btn = ctk.CTkButton(
                row, text=name,
                width=130, height=28,
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_primary"],
                border_width=1, border_color=COLORS["border"],
                corner_radius=6, font=FONTS["small"],
                command=lambda n=name: self._apply_preset(n)
            )
            btn.pack(side="left", padx=4)

    def _param_slider(self, parent, row, col, label, key,
                      mn, mx, default, dtype):
        """Create a labeled slider with linked entry."""
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=row, column=col, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(cell, text=label,
                     font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")

        row_inner = ctk.CTkFrame(cell, fg_color="transparent")
        row_inner.pack(fill="x")

        var = ctk.DoubleVar(value=float(default))
        self._vars[key] = (var, dtype)

        entry = ctk.CTkEntry(
            row_inner, width=70, height=30,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=FONTS["small"]
        )
        entry.insert(0, str(dtype(default)))
        entry.pack(side="right", padx=(6, 0))

        slider = ctk.CTkSlider(
            row_inner, from_=mn, to=mx,
            variable=var,
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_dim"],
            fg_color=COLORS["bg_input"],
            progress_color=COLORS["accent"],
            height=16
        )
        slider.pack(side="left", fill="x", expand=True)

        def on_slider(v):
            val = dtype(float(v))
            entry.delete(0, "end")
            entry.insert(0, str(val))

        def on_entry(event=None):
            try:
                val = dtype(float(entry.get()))
                val = max(mn, min(mx, val))
                var.set(float(val))
            except ValueError:
                pass

        slider.configure(command=on_slider)
        entry.bind("<Return>", on_entry)
        entry.bind("<FocusOut>", on_entry)

    def _param_dropdown(self, parent, col, label, key, options, default):
        """Create a labeled dropdown."""
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=0, column=col, sticky="ew", padx=8, pady=6)

        ctk.CTkLabel(cell, text=label,
                     font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")

        var = ctk.StringVar(value=default)
        self._vars[key] = (var, str)

        color = PROTOCOL_COLORS.get(default, COLORS["accent"]) if key == "protocol" else COLORS["accent"]

        dropdown = ctk.CTkOptionMenu(
            cell, values=options, variable=var,
            fg_color=COLORS["bg_input"],
            button_color=color,
            button_hover_color=COLORS["accent_dim"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["bg_hover"],
            font=FONTS["small"],
            height=32
        )
        dropdown.pack(fill="x", pady=(4, 0))

    def _build_action_buttons(self):
        btn_card = ctk.CTkFrame(self, fg_color="transparent")
        btn_card.pack(fill="x", padx=20, pady=(4, 20))

        # Install/Build button
        self._install_btn = ctk.CTkButton(
            btn_card, text="📦  Install & Build Sim",
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["warning"],
            border_width=1, border_color=COLORS["warning"],
            corner_radius=RADIUS["sm"],
            font=FONTS["subhead"],
            height=40, width=200,
            command=self._on_install
        )
        self._install_btn.pack(side="left", padx=(0, 10))

        # Cancel button
        self._cancel_btn = ctk.CTkButton(
            btn_card, text="⛔  Stop",
            fg_color=COLORS["bg_card"],
            hover_color="#3D1515",
            text_color=COLORS["danger"],
            border_width=1, border_color=COLORS["danger"],
            corner_radius=RADIUS["sm"],
            font=FONTS["subhead"],
            height=40, width=100,
            state="disabled",
            command=self._on_cancel
        )
        self._cancel_btn.pack(side="left", padx=(0, 10))

        # Run button
        self._run_btn = ctk.CTkButton(
            btn_card, text="▶  Run Simulation",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dim"],
            text_color="#000000",
            corner_radius=RADIUS["sm"],
            font=("Segoe UI", 13, "bold"),
            height=44, width=200,
            command=self._do_run
        )
        self._run_btn.pack(side="right")

    # ── Actions ─────────────────────────────────────────────────────────────
    def _do_run(self):
        config = self.get_config()
        self.set_running(True)
        self._on_run(config)

    def get_config(self) -> SimConfig:
        """Read all form values and return a SimConfig."""
        vals = {}
        for key, (var, dtype) in self._vars.items():
            try:
                vals[key] = dtype(var.get()) if dtype != str else var.get()
            except Exception:
                vals[key] = var.get()
        return SimConfig(
            protocol      = vals.get("protocol", "AODV"),
            numNodes      = int(vals.get("numNodes", 20)),
            simTime       = float(vals.get("simTime", 60)),
            areaWidth     = float(vals.get("areaWidth", 1000)),
            areaHeight    = float(vals.get("areaHeight", 1000)),
            speed         = float(vals.get("speed", 10)),
            pauseTime     = float(vals.get("pauseTime", 2)),
            battery       = float(vals.get("battery", 100)),
            txRange       = float(vals.get("txRange", 250)),
            packetSize    = int(vals.get("packetSize", 512)),
            dataRate      = vals.get("dataRate", "2Mbps"),
            mobilityModel = vals.get("mobilityModel", "RandomWaypoint"),
        )

    def _apply_preset(self, name: str):
        preset = self._presets.get(name, {})
        for key, val in preset.items():
            if key in self._vars:
                var, dtype = self._vars[key]
                try:
                    var.set(val if isinstance(var, ctk.StringVar) else float(val))
                except Exception:
                    pass

    def set_running(self, running: bool):
        self._is_running = running
        state_run    = "disabled" if running else "normal"
        state_cancel = "normal"   if running else "disabled"
        self._run_btn.configure(state=state_run)
        self._cancel_btn.configure(state=state_cancel)
        if running:
            self._run_btn.configure(text="⏳  Running...")
        else:
            self._run_btn.configure(text="▶  Run Simulation")
