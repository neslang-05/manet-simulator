"""
ui/theme.py — Centralized design tokens for the MANET platform UI.
"""

# ── Color Tokens ─────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":    "#F5F7FA",
    "bg_secondary":  "#E9ECEF",
    "bg_card":       "#FFFFFF",
    "bg_sidebar":    "#E2E6EA",
    "bg_input":      "#FFFFFF",
    "bg_hover":      "#DDE2E5",
    "bg_active":     "#CED4DA",

    # Accents (Professional deep blue)
    "accent":        "#003366",
    "accent_dim":    "#004488",
    "accent_glow":   "#00336622",
    "success":       "#28A745",
    "warning":       "#FFC107",
    "danger":        "#DC3545",
    "purple":        "#6F42C1",

    # Protocol colors (made dark enough to read on light backgrounds)
    "proto_aodv":    "#004085",
    "proto_dsdv":    "#C82333",
    "proto_dsr":     "#218838",
    "proto_olsr":    "#D39E00",

    # Text
    "text_primary":  "#212529",
    "text_secondary":"#495057",
    "text_muted":    "#6C757D",
    "text_accent":   "#003366",

    # Borders
    "border":        "#DEE2E6",
    "border_active": "#00336688",

    # Links
    "link":          "#0066CC",
    "link_hover":    "#004499",
}

FONTS = {
    "display": ("Arial", 28, "bold"),
    "heading": ("Arial", 20, "bold"),
    "subhead": ("Arial", 16, "bold"),
    "body":    ("Arial", 14),
    "small":   ("Arial", 12),
    "mono":    ("Consolas", 12),
    "mono_lg": ("Consolas", 14),
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
