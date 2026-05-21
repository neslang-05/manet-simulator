"""
ui/panels/history.py — Experiment History Panel
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
from ui.theme import COLORS, FONTS, RADIUS, PROTOCOL_COLORS
from backend.experiment_manager import ExperimentManager


class HistoryPanel(ctk.CTkFrame):
    """Experiment history browser with reload/rerun/delete actions."""

    def __init__(self, parent, on_load_results: Callable,
                 on_rerun: Callable, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._manager       = ExperimentManager()
        self._on_load       = on_load_results
        self._on_rerun      = on_rerun
        self._selected_id   = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 8))
        ctk.CTkLabel(hdr, text="🗂  Experiment History",
                     font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(
            hdr, text="↻ Refresh",
            width=90, height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            border_width=1, border_color=COLORS["accent"],
            corner_radius=6, font=FONTS["small"],
            command=self.refresh
        ).pack(side="right")

        # Action bar
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(0, 10))

        self._view_btn = ctk.CTkButton(
            action_bar, text="📊 View Results",
            state="disabled", height=32,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dim"],
            text_color="#000", corner_radius=RADIUS["sm"],
            font=FONTS["small"],
            command=self._view_selected
        )
        self._view_btn.pack(side="left", padx=(0, 8))

        self._rerun_btn = ctk.CTkButton(
            action_bar, text="▶ Re-run",
            state="disabled", height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["success"],
            border_width=1, border_color=COLORS["success"],
            corner_radius=RADIUS["sm"], font=FONTS["small"],
            command=self._rerun_selected
        )
        self._rerun_btn.pack(side="left", padx=(0, 8))

        self._delete_btn = ctk.CTkButton(
            action_bar, text="🗑 Delete",
            state="disabled", height=32,
            fg_color=COLORS["bg_card"],
            hover_color="#2D1010",
            text_color=COLORS["danger"],
            border_width=1, border_color=COLORS["danger"],
            corner_radius=RADIUS["sm"], font=FONTS["small"],
            command=self._delete_selected
        )
        self._delete_btn.pack(side="left")

        # Experiment list
        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            scrollbar_button_color=COLORS["accent_dim"]
        )
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Column headers
        hdr_row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
        hdr_row.pack(fill="x", padx=12, pady=(8, 0))
        for text, w in [("Timestamp", 160), ("Protocol", 70),
                        ("Nodes", 60), ("Time(s)", 70),
                        ("Status", 80), ("Run ID", 180)]:
            ctk.CTkLabel(hdr_row, text=text, width=w,
                         font=FONTS["small"],
                         text_color=COLORS["text_muted"],
                         anchor="w").pack(side="left", padx=4)

        ctk.CTkFrame(self._list_frame, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=4)

        self._experiment_rows = []

    def refresh(self):
        """Reload and display experiment history."""
        # Clear rows
        for row in self._experiment_rows:
            row.destroy()
        self._experiment_rows = []
        self._selected_id = None
        self._update_buttons()

        experiments = self._manager.get_all()
        if not experiments:
            lbl = ctk.CTkLabel(
                self._list_frame,
                text="No experiments yet. Run a simulation to start.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"]
            )
            lbl.pack(pady=30)
            self._experiment_rows.append(lbl)
            return

        for exp in experiments:
            row = self._build_row(exp)
            self._experiment_rows.append(row)

    def _build_row(self, exp: dict) -> ctk.CTkFrame:
        proto = exp.get("protocol", "?")
        color = PROTOCOL_COLORS.get(proto, COLORS["text_secondary"])
        status_ok = exp.get("success", False)

        row = ctk.CTkFrame(
            self._list_frame,
            fg_color="transparent",
            corner_radius=RADIUS["sm"],
            height=40
        )
        row.pack(fill="x", padx=12, pady=2)

        def select(e=None, eid=exp["id"], r=row):
            self._selected_id = eid
            for rw in self._experiment_rows:
                if hasattr(rw, 'configure'):
                    rw.configure(fg_color="transparent")
            r.configure(fg_color=COLORS["bg_active"])
            self._update_buttons()

        row.bind("<Button-1>", select)

        ts   = exp.get("timestamp", "")[:19].replace("T", " ")
        vals = [
            (ts,                          160, COLORS["text_primary"]),
            (proto,                        70,  color),
            (str(exp.get("numNodes", "")), 60,  COLORS["text_secondary"]),
            (str(exp.get("simTime", "")),  70,  COLORS["text_secondary"]),
            ("✅" if status_ok else "❌",   80,  COLORS["success"] if status_ok else COLORS["danger"]),
            (exp.get("id", ""),            180, COLORS["text_muted"]),
        ]
        for text, w, fc in vals:
            lbl = ctk.CTkLabel(row, text=text, width=w, anchor="w",
                               font=FONTS["small"], text_color=fc)
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", select)

        return row

    def _update_buttons(self):
        state = "normal" if self._selected_id else "disabled"
        self._view_btn.configure(state=state)
        self._rerun_btn.configure(state=state)
        self._delete_btn.configure(state=state)

    def _view_selected(self):
        exp = self._manager.get_by_id(self._selected_id)
        if exp and self._on_load:
            self._on_load(exp.get("output_win", ""),
                          exp.get("protocol", "N/A"))

    def _rerun_selected(self):
        exp = self._manager.get_by_id(self._selected_id)
        if exp and self._on_rerun:
            self._on_rerun(exp.get("config", {}))

    def _delete_selected(self):
        if not self._selected_id:
            return
        if messagebox.askyesno("Delete",
                               f"Delete experiment {self._selected_id}?"):
            self._manager.delete(self._selected_id)
            self._selected_id = None
            self.refresh()

    def add_experiment(self, result: dict):
        """Save a new experiment result and refresh the list."""
        self._manager.save(result)
        self.refresh()
