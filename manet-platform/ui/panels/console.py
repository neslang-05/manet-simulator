"""
ui/panels/console.py — Real-Time Console Log Panel
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from ui.theme import COLORS, FONTS, RADIUS


class ConsolePanel(ctk.CTkFrame):
    """Real-time scrolling simulation log console."""

    LOG_COLORS = {
        "ERROR":   "#FF6B6B",
        "WARNING": "#FFD43B",
        "SUCCESS": "#51CF66",
        "INFO":    "#8B91A8",
        "SIM":     "#00C6FF",
        "WSL":     "#9775FA",
        "DEFAULT": "#C5C9D8",
    }

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._auto_scroll = True
        self._build_ui()

    def _build_ui(self):
        # Header bar
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                           corner_radius=0, height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="⬛  Console Output",
                     font=FONTS["subhead"],
                     text_color=COLORS["text_primary"]).pack(side="left", padx=16)

        # Controls
        ctrl_row = ctk.CTkFrame(hdr, fg_color="transparent")
        ctrl_row.pack(side="right", padx=12)

        self._scroll_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            ctrl_row, text="Auto-scroll",
            variable=self._scroll_var,
            checkbox_width=16, checkbox_height=16,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dim"],
            command=lambda: setattr(self, '_auto_scroll', self._scroll_var.get())
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            ctrl_row, text="Clear",
            width=60, height=26,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=FONTS["small"],
            corner_radius=5,
            command=self.clear
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            ctrl_row, text="Copy",
            width=60, height=26,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=FONTS["small"],
            corner_radius=5,
            command=self._copy_all
        ).pack(side="left", padx=4)

        # Text area
        text_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"],
                                  corner_radius=0)
        text_frame.pack(fill="both", expand=True, padx=1, pady=(1, 0))

        self._text = tk.Text(
            text_frame,
            bg=COLORS["bg_primary"],
            fg=self.LOG_COLORS["DEFAULT"],
            font=FONTS["mono"],
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["bg_active"],
            selectforeground=COLORS["text_primary"],
            relief="flat",
            borderwidth=0,
            wrap="word",
            state="disabled",
            padx=12,
            pady=8
        )

        scrollbar = tk.Scrollbar(text_frame, command=self._text.yview,
                                 bg=COLORS["bg_card"],
                                 troughcolor=COLORS["bg_primary"],
                                 activebackground=COLORS["accent"])
        self._text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._text.pack(side="left", fill="both", expand=True)

        # Configure color tags
        for tag, color in self.LOG_COLORS.items():
            self._text.tag_configure(tag, foreground=color)
        self._text.tag_configure("TIMESTAMP", foreground=COLORS["text_muted"])
        self._text.tag_configure("BOLD", font=FONTS["mono_lg"])

    def _detect_tag(self, line: str) -> str:
        """Detect log level tag from line content."""
        upper = line.upper()
        if "[ERROR]" in upper or "error" in line.lower():
            return "ERROR"
        elif "[WARNING]" in upper or "warn" in line.lower():
            return "WARNING"
        elif "[SUCCESS]" in upper or "done" in line.lower() or "successful" in line.lower():
            return "SUCCESS"
        elif "[WSL]" in upper:
            return "WSL"
        elif "[RUNNER]" in upper or "[MANE" in upper or "[SIM" in upper:
            return "SIM"
        return "DEFAULT"

    def log(self, line: str, tag: str = None):
        """Append a line to the console."""
        if not tag:
            tag = self._detect_tag(line)
        ts = datetime.now().strftime("%H:%M:%S")

        self._text.configure(state="normal")
        self._text.insert("end", f"[{ts}] ", "TIMESTAMP")
        self._text.insert("end", line + "\n", tag)
        self._text.configure(state="disabled")

        if self._auto_scroll:
            self._text.see("end")

    def log_success(self, msg: str):
        self.log(msg, "SUCCESS")

    def log_error(self, msg: str):
        self.log(msg, "ERROR")

    def log_info(self, msg: str):
        self.log(msg, "INFO")

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def _copy_all(self):
        content = self._text.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(content)
