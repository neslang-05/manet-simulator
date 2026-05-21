"""
ui/app.py — Main Application Window
CustomTkinter-based MANET Research Platform GUI.
"""

import customtkinter as ctk
import threading
import os
from pathlib import Path
from typing import Optional

from ui.theme import COLORS, FONTS, SPACING, RADIUS, PROTOCOL_COLORS
from ui.panels.simulation  import SimulationPanel
from ui.panels.console     import ConsolePanel
from ui.panels.results     import ResultsPanel
from ui.panels.graphs      import GraphsPanel
from ui.panels.history     import HistoryPanel
from ui.panels.comparison  import ComparisonPanel
from ui.panels.diagnostics import DiagnosticsPanel

from backend.sim_runner       import SimRunner, SimConfig
from backend.wsl_bridge       import WSLBridge
from backend.experiment_manager import ExperimentManager
from analysis.graph_generator import GraphGenerator


# ── Sidebar navigation items ────────────────────────────────────────────────
NAV_ITEMS = [
    ("simulation",  "⚙",  "Simulation"),
    ("console",     "▶",  "Console"),
    ("results",     "📊",  "Results"),
    ("graphs",      "📈",  "Graphs"),
    ("history",     "🗂",  "History"),
    ("comparison",  "⚖",  "Comparison"),
    ("diagnostics", "🔧",  "Diagnostics"),
]


class ManetApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────────────────────────
        self.title("MANET Research & Visualization Platform")
        self.geometry("1400x900")
        self.minsize(1200, 750)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=COLORS["bg_primary"])

        # ── Backend ───────────────────────────────────────────────────────
        self._runner = SimRunner()
        self._exp_mgr = ExperimentManager()
        self._latest_result: Optional[dict] = None

        # ── Layout ────────────────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_status_bar()

        # ── Initial navigation ────────────────────────────────────────────
        self._active_panel = None
        self._panel_widgets = {}
        self._build_panels()
        self.navigate_to("simulation")

        # ── Run startup diagnostics ───────────────────────────────────────
        self.after(1000, self._run_startup_checks)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self, width=220, fg_color=COLORS["bg_sidebar"],
            corner_radius=0
        )
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(len(NAV_ITEMS) + 2, weight=1)

        # Logo area
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame, text="MANET\nPlatform",
            font=("Arial", 18, "bold"),
            text_color=COLORS["accent"],
            justify="left"
        ).place(x=20, y=15)

        ctk.CTkLabel(
            logo_frame, text="Research Suite",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).place(x=20, y=65)

        # Divider
        ctk.CTkFrame(self._sidebar, height=1,
                     fg_color=COLORS["border"]).pack(fill="x")

        # Nav buttons
        self._nav_buttons = {}
        for key, icon, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=42,
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_secondary"],
                font=FONTS["body"],
                corner_radius=0,
                command=lambda k=key: self.navigate_to(k)
            )
            btn.pack(fill="x", pady=1)
            self._nav_buttons[key] = btn

        # Bottom: version
        ctk.CTkLabel(
            self._sidebar,
            text="v1.0.0  |  NS-3 + NetAnim",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(side="bottom", pady=12)

        # WSL status dot
        self._wsl_dot = ctk.CTkLabel(
            self._sidebar, text="⬤  WSL: Checking...",
            font=FONTS["small"], text_color=COLORS["warning"]
        )
        self._wsl_dot.pack(side="bottom", pady=0, padx=16, anchor="w")

    # ── Main content area ─────────────────────────────────────────────────────
    def _build_main_area(self):
        self._content = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=0
        )
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

    def _build_status_bar(self):
        self._statusbar = ctk.CTkFrame(
            self, height=28, fg_color=COLORS["bg_card"], corner_radius=0
        )
        self._statusbar.grid(row=1, column=1, sticky="ew")
        self._statusbar.grid_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            self._statusbar, text="Ready",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        self._status_lbl.pack(side="left", padx=14)

        self._progress = ctk.CTkProgressBar(
            self._statusbar, width=200,
            progress_color=COLORS["accent"],
            fg_color=COLORS["bg_input"],
            height=6
        )
        self._progress.pack(side="right", padx=14, pady=9)
        self._progress.set(0)

    # ── Build panels ──────────────────────────────────────────────────────────
    def _build_panels(self):
        # Simulation Panel
        self._sim_panel = SimulationPanel(
            self._content,
            on_run=self._on_run_simulation,
            on_cancel=self._on_cancel_simulation,
            on_install=self._on_install_sim
        )

        # Console Panel
        self._console_panel = ConsolePanel(self._content)

        # Results Panel
        self._results_panel = ResultsPanel(self._content)

        # Graphs Panel
        self._graphs_panel = GraphsPanel(self._content)

        # History Panel
        self._history_panel = HistoryPanel(
            self._content,
            on_load_results=self._on_load_results,
            on_rerun=self._on_rerun
        )

        # Comparison Panel
        self._comparison_panel = ComparisonPanel(self._content)

        # Diagnostics Panel
        self._diagnostics_panel = DiagnosticsPanel(
            self._content, console=self._console_panel
        )

        self._panel_widgets = {
            "simulation":  self._sim_panel,
            "console":     self._console_panel,
            "results":     self._results_panel,
            "graphs":      self._graphs_panel,
            "history":     self._history_panel,
            "comparison":  self._comparison_panel,
            "diagnostics": self._diagnostics_panel,
        }

    # ── Navigation ────────────────────────────────────────────────────────────
    def navigate_to(self, key: str):
        """Switch to the specified panel."""
        if self._active_panel:
            self._panel_widgets[self._active_panel].grid_forget()

        # Update nav button styles
        for k, btn in self._nav_buttons.items():
            active = k == key
            btn.configure(
                fg_color=COLORS["bg_active"] if active else "transparent",
                text_color=COLORS["accent"] if active else COLORS["text_secondary"]
            )

        self._panel_widgets[key].grid(row=0, column=0, sticky="nsew")
        self._active_panel = key
        self._set_status(f"📍 {key.capitalize()}")

    # ── Simulation lifecycle ──────────────────────────────────────────────────
    def _on_install_sim(self):
        """Install and build manet-sim.cc via WSL."""
        self.navigate_to("diagnostics")
        self._diagnostics_panel._do_install()

    def _on_run_simulation(self, config: SimConfig):
        """Launch NS-3 simulation."""
        self._runner.set_config(config)
        self._console_panel.clear()
        self.navigate_to("console")
        self._set_status("⏳ Simulation running...")
        self._progress.set(0.1)
        self._start_progress_animation()

        self._runner.run(
            on_log=self._handle_log,
            on_done=self._handle_sim_done
        )

    def _on_cancel_simulation(self):
        self._runner.cancel()
        self._sim_panel.set_running(False)
        self._set_status("⚠ Simulation cancelled")
        self._progress.set(0)

    def _handle_log(self, line: str):
        """Thread-safe log to console."""
        self.after(0, lambda: self._console_panel.log(line))

    def _handle_sim_done(self, success: bool, result: dict):
        """Called when simulation finishes."""
        self._latest_result = result

        def _finish():
            self._sim_panel.set_running(False)
            self._progress.set(0)
            self._stop_progress_animation()

            if success:
                self._console_panel.log_success("✅ Simulation completed!")
                self._set_status("✅ Simulation complete — generating graphs...")

                # Save to history
                self._history_panel.add_experiment(result)

                # Generate graphs
                output_win = result.get("output_win", "")
                if output_win and Path(output_win).exists():
                    self._generate_graphs(output_win,
                                         result.get("config", {}).get("protocol", "AODV"))

                # Open NetAnim
                xml_wsl = result.get("output_wsl", "") + "/manet-animation.xml"
                self._runner.bridge.launch_netanim(xml_wsl)
            else:
                self._console_panel.log_error("❌ Simulation failed.")
                self._set_status("❌ Simulation failed")

        self.after(0, _finish)

    def _generate_graphs(self, output_dir: str, protocol: str):
        """Generate all analysis graphs in background thread."""
        def _worker():
            try:
                gen = GraphGenerator(output_dir, protocol)
                paths = gen.generate_all()
                graphs_dir = str(Path(output_dir) / "graphs")

                def _update_ui():
                    self._graphs_panel.load_graphs(graphs_dir)
                    self._results_panel.load_results(output_dir, protocol)
                    self._set_status(f"✅ Done — {len(paths)} graphs generated")

                self.after(0, _update_ui)
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Graph error: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_load_results(self, output_dir: str, protocol: str):
        """Load experiment results from history."""
        if output_dir and Path(output_dir).exists():
            graphs_dir = str(Path(output_dir) / "graphs")
            self._results_panel.load_results(output_dir, protocol)
            if Path(graphs_dir).exists():
                self._graphs_panel.load_graphs(graphs_dir)
            self.navigate_to("results")
        else:
            self._console_panel.log_error(
                f"[App] Output directory not found: {output_dir}"
            )

    def _on_rerun(self, config_dict: dict):
        """Re-run an experiment from history."""
        from dataclasses import fields
        config = SimConfig()
        for f in fields(config):
            if f.name in config_dict:
                try:
                    setattr(config, f.name, type(getattr(config, f.name))(config_dict[f.name]))
                except Exception:
                    pass
        self.navigate_to("simulation")
        self.after(200, lambda: self._on_run_simulation(config))

    # ── Status / progress ─────────────────────────────────────────────────────
    def _set_status(self, msg: str):
        self._status_lbl.configure(text=msg)

    def _progress_tick(self):
        current = self._progress.get()
        next_val = current + 0.02
        if next_val >= 0.9:
            next_val = 0.2
        self._progress.set(next_val)
        if self._animating:
            self.after(200, self._progress_tick)

    def _start_progress_animation(self):
        self._animating = True
        self._progress_tick()

    def _stop_progress_animation(self):
        self._animating = False
        self._progress.set(0)

    # ── Startup ───────────────────────────────────────────────────────────────
    def _run_startup_checks(self):
        """Quick WSL availability check on startup."""
        def _check():
            bridge = WSLBridge()
            ok, msg = bridge.check_wsl()
            def _update():
                if ok:
                    self._wsl_dot.configure(
                        text="⬤  WSL: Connected",
                        text_color=COLORS["success"]
                    )
                else:
                    self._wsl_dot.configure(
                        text="⬤  WSL: Unavailable",
                        text_color=COLORS["danger"]
                    )
                
                # Auto-load latest experiment if available
                exps = self._history_panel._manager.get_all()
                if exps:
                    latest = exps[0]
                    self._on_load_results(latest.get("output_win", ""), latest.get("protocol", "?"))
                    self.navigate_to("simulation") # Stay on simulation tab on launch

            self.after(0, _update)
        threading.Thread(target=_check, daemon=True).start()
