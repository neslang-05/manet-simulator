"""
ui/widgets/stat_card.py — Metric summary card widget.
"""

import customtkinter as ctk
from ui.theme import COLORS, FONTS, RADIUS


class StatCard(ctk.CTkFrame):
    """A premium stat/metric display card."""

    def __init__(self, parent, title: str, value: str = "--",
                 unit: str = "", accent: str = None, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", RADIUS["md"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(parent, **kwargs)

        self._accent = accent or COLORS["accent"]

        # Accent bar on top
        self._bar = ctk.CTkFrame(
            self, height=3, fg_color=self._accent,
            corner_radius=0
        )
        self._bar.pack(fill="x", pady=(0, 0))

        # Content
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=(10, 12))

        self._title_lbl = ctk.CTkLabel(
            inner, text=title,
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self._title_lbl.pack(fill="x")

        val_row = ctk.CTkFrame(inner, fg_color="transparent")
        val_row.pack(fill="x", pady=(2, 0))

        self._value_lbl = ctk.CTkLabel(
            val_row, text=value,
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self._value_lbl.pack(side="left")

        if unit:
            self._unit_lbl = ctk.CTkLabel(
                val_row, text=f" {unit}",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            self._unit_lbl.pack(side="left", pady=(6, 0))

    def update_value(self, value: str, unit: str = None):
        """Update the displayed value."""
        self._value_lbl.configure(text=value)
        if unit is not None and hasattr(self, '_unit_lbl'):
            self._unit_lbl.configure(text=f" {unit}")

    def set_accent(self, color: str):
        """Change the accent color."""
        self._accent = color
        self._bar.configure(fg_color=color)
