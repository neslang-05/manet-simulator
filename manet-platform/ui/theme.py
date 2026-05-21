"""
ui/theme.py — Centralized design tokens for the MANET platform UI.
"""

# ── Color Tokens ─────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":    "#0B0D14",
    "bg_secondary":  "#111320",
    "bg_card":       "#161926",
    "bg_sidebar":    "#0D0F1A",
    "bg_input":      "#1C1F2E",
    "bg_hover":      "#1E2235",
    "bg_active":     "#252A3D",

    # Accents
    "accent":        "#00C6FF",
    "accent_dim":    "#0099CC",
    "accent_glow":   "#00C6FF22",
    "success":       "#51CF66",
    "warning":       "#FFD43B",
    "danger":        "#FF6B6B",
    "purple":        "#9775FA",

    # Protocol colors
    "proto_aodv":    "#00C6FF",
    "proto_dsdv":    "#FF6B6B",
    "proto_dsr":     "#51CF66",
    "proto_olsr":    "#FFD43B",

    # Text
    "text_primary":  "#E8EAF0",
    "text_secondary":"#8B91A8",
    "text_muted":    "#4A4F66",
    "text_accent":   "#00C6FF",

    # Borders
    "border":        "#222535",
    "border_active": "#00C6FF44",
}

FONTS = {
    "display": ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 15, "bold"),
    "subhead": ("Segoe UI", 12, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 10),
    "mono":    ("Consolas", 10),
    "mono_lg": ("Consolas", 11),
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 14,
    "lg": 20,
    "xl": 32,
}

RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
    "xl": 20,
}

PROTOCOL_COLORS = {
    "AODV": COLORS["proto_aodv"],
    "DSDV": COLORS["proto_dsdv"],
    "DSR":  COLORS["proto_dsr"],
    "OLSR": COLORS["proto_olsr"],
}
