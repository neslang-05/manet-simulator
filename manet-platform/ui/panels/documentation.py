"""
ui/panels/documentation.py — Documentation & Reference Panel

Shows project documentation, GitHub repository link, protocol reference,
parameter table, quick-start guide, and output file reference.
Repository: https://github.com/neslang-05/manet-simulator
"""

import customtkinter as ctk
import webbrowser
from ui.theme import COLORS, FONTS, SPACING, RADIUS, PROTOCOL_COLORS

REPO_URL = "https://github.com/neslang-05/manet-simulator"
ISSUES_URL = "https://github.com/neslang-05/manet-simulator/issues"
GUIDE_URL = "https://github.com/neslang-05/manet-simulator/blob/main/guide/manet_lab_guide.tex"

PROTOCOL_INFO = [
    (
        "AODV",
        "Ad-hoc On-Demand Distance Vector",
        "Reactive — discovers routes on demand. Low overhead, ideal for moderate-density\n"
        "networks with typical mobility. Routes are invalidated when links break.",
        PROTOCOL_COLORS["AODV"],
    ),
    (
        "DSDV",
        "Destination-Sequenced Distance Vector",
        "Proactive — maintains a full routing table at all times. Consistent routes but\n"
        "higher control overhead. Best for low-mobility, stable topologies.",
        PROTOCOL_COLORS["DSDV"],
    ),
    (
        "DSR",
        "Dynamic Source Routing",
        "Reactive / source-routing — full path embedded in packet header. No routing table\n"
        "at intermediate nodes. Low overhead for small (< 20 nodes) networks.",
        PROTOCOL_COLORS["DSR"],
    ),
    (
        "OLSR",
        "Optimized Link State Routing",
        "Proactive — uses Multipoint Relays (MPRs) to reduce broadcast flooding. Scales\n"
        "well for large, dense networks with frequent topology changes.",
        PROTOCOL_COLORS["OLSR"],
    ),
]

PARAM_ROWS = [
    ("Number of Nodes",  "5 – 100",      "20",      "Network size / density"),
    ("Simulation Time",  "10 – 600 s",   "60 s",    "Total run duration"),
    ("Area Width",       "200 – 5000 m", "1000 m",  "Horizontal simulation field"),
    ("Area Height",      "200 – 5000 m", "1000 m",  "Vertical simulation field"),
    ("Node Speed",       "1 – 50 m/s",   "10 m/s",  "Random waypoint max speed"),
    ("Pause Time",       "0 – 30 s",     "2 s",     "Pause between waypoints"),
    ("Battery Capacity", "10 – 500 J",   "100 J",   "Initial energy per node"),
    ("TX Range",         "50 – 1000 m",  "250 m",   "Wireless transmission range"),
    ("Packet Size",      "64 – 4096 B",  "512 B",   "CBR payload size"),
    ("Data Rate",        "512K – 10M",   "2 Mbps",  "CBR traffic injection rate"),
]

OUTPUT_FILES = [
    ("battery.csv",         "Per-node energy level over time"),
    ("mobility.csv",        "Node X,Y positions over time"),
    ("throughput.csv",      "PDR + throughput sampled over time"),
    ("flowstats.csv",       "Per-flow FlowMonitor statistics"),
    ("summary.csv",         "Single-row aggregate summary"),
    ("manet-animation.xml", "NetAnim animation trace file"),
    ("manet-*.pcap",        "Wireshark-compatible packet captures"),
    ("graphs/*.png",        "8 auto-generated analysis graphs"),
]

QUICK_STEPS = [
    ("1", "Clone", f"git clone {REPO_URL}"),
    ("2", "Install Python deps", "pip install customtkinter matplotlib pandas numpy Pillow"),
    ("3", "Build NS-3 sim file", "Diagnostics panel → Install & Build manet-sim"),
    ("4", "Run the platform", "python manet-platform/main.py"),
    ("5", "Simulate!", "Simulation panel → choose protocol → Run Simulation"),
]


def _open_url(url: str):
    webbrowser.open(url)


class DocumentationPanel(ctk.CTkFrame):
    """Full-featured documentation and reference panel."""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._build_ui()

    # ── Build ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Scrollable wrapper
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self._scroll.pack(fill="both", expand=True, padx=0, pady=0)
        self._scroll.columnconfigure(0, weight=1)

        row = 0
        row = self._hero(row)
        row = self._quick_start(row)
        row = self._section_divider(row, "📡  Protocol Reference")
        row = self._protocol_cards(row)
        row = self._section_divider(row, "⚙  Simulation Parameters")
        row = self._param_table(row)
        row = self._section_divider(row, "📁  Output Files")
        row = self._output_table(row)
        row = self._section_divider(row, "🔗  Resources & Links")
        row = self._links_section(row)

    # ── Hero ─────────────────────────────────────────────────────────────────
    def _hero(self, row: int) -> int:
        hero = ctk.CTkFrame(
            self._scroll,
            fg_color=COLORS["accent"],
            corner_radius=RADIUS["lg"],
        )
        hero.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 8))

        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(
            inner,
            text="MANET Research & Visualization Platform",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text="NS-3  ·  NetAnim  ·  Python / CustomTkinter  ·  WSL2 Ubuntu",
            font=FONTS["body"],
            text_color="#AACCEE",
            anchor="w",
        ).pack(anchor="w", pady=(4, 12))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(anchor="w")

        ctk.CTkButton(
            btn_row,
            text="⭐  View on GitHub",
            font=FONTS["small"],
            fg_color="#FFFFFF",
            hover_color="#E0E0E0",
            text_color=COLORS["accent"],
            corner_radius=RADIUS["sm"],
            height=32,
            width=160,
            command=lambda: _open_url(REPO_URL),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="🐛  Report Issue",
            font=FONTS["small"],
            fg_color="transparent",
            hover_color="#004488",
            text_color="#AACCEE",
            border_width=1,
            border_color="#AACCEE",
            corner_radius=RADIUS["sm"],
            height=32,
            width=140,
            command=lambda: _open_url(ISSUES_URL),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text="📄  LaTeX Guide (.tex)",
            font=FONTS["small"],
            fg_color="transparent",
            hover_color="#004488",
            text_color="#AACCEE",
            border_width=1,
            border_color="#AACCEE",
            corner_radius=RADIUS["sm"],
            height=32,
            width=160,
            command=lambda: _open_url(GUIDE_URL),
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text=REPO_URL,
            font=FONTS["small"],
            text_color="#6699CC",
            anchor="w",
            cursor="hand2",
        ).pack(anchor="w", pady=(10, 0))

        return row + 1

    # ── Quick Start ──────────────────────────────────────────────────────────
    def _quick_start(self, row: int) -> int:
        card = self._card(row, title="🚀  Quick Start")

        for num, title, cmd in QUICK_STEPS:
            step_frame = ctk.CTkFrame(card, fg_color="transparent")
            step_frame.pack(fill="x", padx=16, pady=4)

            # Step number badge
            badge = ctk.CTkFrame(
                step_frame,
                width=28,
                height=28,
                fg_color=COLORS["accent"],
                corner_radius=14,
            )
            badge.pack(side="left", padx=(0, 10))
            badge.pack_propagate(False)
            ctk.CTkLabel(
                badge,
                text=num,
                font=("Arial", 11, "bold"),
                text_color="#FFFFFF",
            ).place(relx=0.5, rely=0.5, anchor="center")

            txt = ctk.CTkFrame(step_frame, fg_color="transparent")
            txt.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                txt,
                text=title,
                font=("Arial", 13, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                txt,
                text=cmd,
                font=FONTS["mono"],
                text_color=COLORS["accent"],
                anchor="w",
            ).pack(anchor="w")

        return row + 1

    # ── Protocol Cards ───────────────────────────────────────────────────────
    def _protocol_cards(self, row: int) -> int:
        grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grid.grid(row=row, column=0, sticky="ew", padx=20, pady=4)
        grid.columnconfigure((0, 1), weight=1)

        for i, (abbr, full, desc, color) in enumerate(PROTOCOL_INFO):
            r, c = divmod(i, 2)
            card = ctk.CTkFrame(
                grid,
                fg_color=COLORS["bg_card"],
                corner_radius=RADIUS["md"],
                border_width=2,
                border_color=color,
            )
            card.grid(row=r, column=c, padx=8, pady=8, sticky="ew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=14)

            header = ctk.CTkFrame(inner, fg_color="transparent")
            header.pack(fill="x", pady=(0, 6))

            tag = ctk.CTkFrame(
                header,
                fg_color=color,
                corner_radius=RADIUS["sm"],
                width=56,
                height=26,
            )
            tag.pack(side="left", padx=(0, 8))
            tag.pack_propagate(False)
            ctk.CTkLabel(
                tag,
                text=abbr,
                font=("Arial", 12, "bold"),
                text_color="#FFFFFF",
            ).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                header,
                text=full,
                font=("Arial", 12, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w",
                wraplength=260,
            ).pack(side="left")

            ctk.CTkLabel(
                inner,
                text=desc,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
                justify="left",
                wraplength=320,
            ).pack(anchor="w")

        return row + 1

    # ── Parameter Table ──────────────────────────────────────────────────────
    def _param_table(self, row: int) -> int:
        card = self._card(row, title=None)

        # Header row
        self._table_row(
            card,
            ("Parameter", "Range", "Default", "Description"),
            is_header=True,
        )

        for i, cols in enumerate(PARAM_ROWS):
            self._table_row(card, cols, is_header=False, shaded=(i % 2 == 0))

        return row + 1

    def _table_row(self, parent, cols, is_header=False, shaded=False):
        widths = [180, 110, 80, 0]  # 0 = expand
        bg = COLORS["bg_secondary"] if (shaded and not is_header) else COLORS["bg_card"]
        font = ("Arial", 12, "bold") if is_header else FONTS["small"]
        color = COLORS["accent"] if is_header else COLORS["text_primary"]

        row_frame = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
        row_frame.pack(fill="x", padx=0)

        for j, (text, width) in enumerate(zip(cols, widths)):
            kw = {"width": width} if width else {}
            expand = width == 0
            ctk.CTkLabel(
                row_frame,
                text=text,
                font=font,
                text_color=color,
                anchor="w",
                **kw,
            ).pack(side="left", padx=10, pady=6, fill="x" if expand else None,
                   expand=expand)

    # ── Output Files Table ───────────────────────────────────────────────────
    def _output_table(self, row: int) -> int:
        card = self._card(row, title=None)

        self._table_row(card, ("File", "Description", "", ""), is_header=True)

        for i, (fname, desc) in enumerate(OUTPUT_FILES):
            bg = COLORS["bg_secondary"] if i % 2 == 0 else COLORS["bg_card"]
            rf = ctk.CTkFrame(card, fg_color=bg, corner_radius=0)
            rf.pack(fill="x")

            ctk.CTkLabel(
                rf,
                text=fname,
                font=FONTS["mono"],
                text_color=COLORS["accent"],
                anchor="w",
                width=200,
            ).pack(side="left", padx=10, pady=6)

            ctk.CTkLabel(
                rf,
                text=desc,
                font=FONTS["small"],
                text_color=COLORS["text_secondary"],
                anchor="w",
            ).pack(side="left", padx=6, pady=6, fill="x", expand=True)

        return row + 1

    # ── Links Section ────────────────────────────────────────────────────────
    def _links_section(self, row: int) -> int:
        card = self._card(row, title=None)

        links = [
            ("📦  Repository", REPO_URL, "Browse source code, releases, and commits"),
            ("🐛  Issues", ISSUES_URL, "Report bugs or request new features"),
            ("📄  LaTeX Guide", GUIDE_URL, "Full setup and simulation guide (.tex source)"),
        ]

        for label, url, desc in links:
            rf = ctk.CTkFrame(card, fg_color="transparent")
            rf.pack(fill="x", padx=16, pady=6)

            btn = ctk.CTkButton(
                rf,
                text=label,
                font=("Arial", 12, "bold"),
                fg_color=COLORS["bg_secondary"],
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["link"],
                anchor="w",
                width=200,
                height=32,
                corner_radius=RADIUS["sm"],
                border_width=1,
                border_color=COLORS["border"],
                command=lambda u=url: _open_url(u),
            )
            btn.pack(side="left", padx=(0, 12))

            ctk.CTkLabel(
                rf,
                text=desc,
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

        # Version footer
        ctk.CTkLabel(
            card,
            text="v1.1.0  ·  NS-3 + NetAnim  ·  github.com/neslang-05/manet-simulator",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="center",
        ).pack(pady=(12, 16))

        return row + 1

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _card(self, row: int, title=None) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self._scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=row, column=0, sticky="ew", padx=20, pady=4)

        if title:
            ctk.CTkLabel(
                card,
                text=title,
                font=FONTS["subhead"],
                text_color=COLORS["accent"],
                anchor="w",
            ).pack(anchor="w", padx=16, pady=(14, 8))

            # Divider
            ctk.CTkFrame(card, height=1, fg_color=COLORS["border"]).pack(fill="x")

        return card

    def _section_divider(self, row: int, text: str) -> int:
        div = ctk.CTkFrame(self._scroll, fg_color="transparent")
        div.grid(row=row, column=0, sticky="ew", padx=20, pady=(18, 2))

        ctk.CTkLabel(
            div,
            text=text,
            font=FONTS["subhead"],
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(side="left")

        ctk.CTkFrame(div, height=1, fg_color=COLORS["border"]).pack(
            side="left", fill="x", expand=True, padx=(12, 0), pady=8
        )

        return row + 1
