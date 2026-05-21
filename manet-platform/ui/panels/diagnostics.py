"""
ui/panels/diagnostics.py — WSL Diagnostics Panel
"""

import customtkinter as ctk
import threading
from ui.theme import COLORS, FONTS, RADIUS
from backend.wsl_bridge import WSLBridge


DIAG_ITEMS = [
    ("wsl",       "WSL 2 Connected"),
    ("ns3",       "NS-3 Available"),
    ("netanim",   "NetAnim Available"),
    ("sim",       "manet-sim.cc Installed"),
]


class DiagnosticsPanel(ctk.CTkFrame):
    """WSL environment diagnostics panel."""

    def __init__(self, parent, console=None, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._bridge  = WSLBridge()
        self._console = console
        self._status  = {}
        self._build_ui()
        self.after(500, self.run_diagnostics)

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 12))
        ctk.CTkLabel(hdr, text="🔧  WSL Diagnostics",
                     font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(
            hdr, text="↻  Refresh",
            width=100, height=32,
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            border_width=1, border_color=COLORS["accent"],
            corner_radius=6, font=FONTS["small"],
            command=self.run_diagnostics
        ).pack(side="right")

        # Status cards
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=(0, 12))
        cards_frame.columnconfigure((0, 1), weight=1)

        self._status_labels  = {}
        self._status_dots    = {}
        self._status_details = {}

        for i, (key, label) in enumerate(DIAG_ITEMS):
            r, c = divmod(i, 2)
            card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_card"],
                                corner_radius=RADIUS["md"],
                                border_width=1, border_color=COLORS["border"])
            card.grid(row=r, column=c, padx=8, pady=8, sticky="ew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=12)

            dot = ctk.CTkLabel(inner, text="⬤", font=("Segoe UI", 14),
                               text_color=COLORS["text_muted"], width=20)
            dot.pack(side="left", padx=(0, 8))
            self._status_dots[key] = dot

            txt_col = ctk.CTkFrame(inner, fg_color="transparent")
            txt_col.pack(side="left", fill="x", expand=True)

            lbl = ctk.CTkLabel(txt_col, text=label, font=FONTS["subhead"],
                               text_color=COLORS["text_primary"], anchor="w")
            lbl.pack(anchor="w")
            self._status_labels[key] = lbl

            detail = ctk.CTkLabel(txt_col, text="Checking...",
                                  font=FONTS["small"],
                                  text_color=COLORS["text_secondary"], anchor="w")
            detail.pack(anchor="w")
            self._status_details[key] = detail

        # Install section
        install_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                    corner_radius=RADIUS["md"],
                                    border_width=1, border_color=COLORS["border"])
        install_card.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(install_card, text="Setup Actions",
                     font=FONTS["subhead"],
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(14, 8))

        btn_row = ctk.CTkFrame(install_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            btn_row, text="📦  Install & Build manet-sim",
            fg_color=COLORS["accent"], hover_color=COLORS["accent_dim"],
            text_color="#000", corner_radius=RADIUS["sm"],
            font=FONTS["subhead"], height=38,
            command=self._do_install
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="🔍  Show NS-3 Version",
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=RADIUS["sm"], font=FONTS["small"],
            height=38, width=180,
            command=self._show_ns3_version
        ).pack(side="left")

        # Log area
        self._log = ctk.CTkTextbox(
            self, height=180,
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["text_secondary"],
            font=FONTS["mono"],
            corner_radius=RADIUS["sm"]
        )
        self._log.pack(fill="x", padx=20, pady=(0, 20))

    def _set_status(self, key: str, ok: bool, msg: str):
        color  = COLORS["success"] if ok else COLORS["danger"]
        self._status_dots[key].configure(text_color=color)
        self._status_details[key].configure(
            text=msg, text_color=COLORS["text_secondary"]
        )
        self._status[key] = ok

    def _append_log(self, msg: str):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.configure(state="disabled")
        self._log.see("end")

    def run_diagnostics(self):
        """Run all environment checks in background thread."""
        for key, _ in DIAG_ITEMS:
            self._status_dots[key].configure(text_color=COLORS["warning"])
            self._status_details[key].configure(text="Checking...")

        def _worker():
            ok, msg = self._bridge.check_wsl()
            self.after(0, lambda: self._set_status("wsl", ok, msg))

            ok, msg = self._bridge.check_ns3()
            self.after(0, lambda: self._set_status("ns3", ok, msg))

            ok, msg = self._bridge.check_netanim()
            self.after(0, lambda: self._set_status("netanim", ok, msg))

            ok, msg = self._bridge.check_sim_installed()
            self.after(0, lambda: self._set_status("sim", ok, msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _do_install(self):
        import os
        from pathlib import Path
        cc_path = str(Path(__file__).parent.parent.parent / "ns3" / "manet-sim.cc")
        self._append_log("Starting install...")

        def on_out(line):
            self.after(0, lambda: self._append_log(line))

        def on_done(rc):
            msg = "Install complete!" if rc == 0 else f"Install failed (code {rc})"
            self.after(0, lambda: self._append_log(msg))
            self.after(0, self.run_diagnostics)

        self._bridge.install_sim(cc_path, on_out, on_done)

    def _show_ns3_version(self):
        def _worker():
            ok, out = self._bridge.run_sync(
                f"cd ~/ns-3-dev && ./ns3 --version 2>&1"
            )
            self.after(0, lambda: self._append_log(out))
        threading.Thread(target=_worker, daemon=True).start()

    def get_status(self) -> dict:
        return dict(self._status)
