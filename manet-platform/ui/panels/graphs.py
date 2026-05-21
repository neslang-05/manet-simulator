"""
ui/panels/graphs.py — Graph Viewer Panel
Embeds Matplotlib figures inside the CustomTkinter UI.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image
from ui.theme import COLORS, FONTS, RADIUS


GRAPH_LABELS = {
    "battery_over_time":  "🔋 Battery Over Time",
    "pdr_over_time":      "📦 PDR Over Time",
    "throughput_over_time": "📡 Throughput",
    "node_density":       "🗺 Node Density",
    "area_coverage":      "📐 Area Coverage",
    "energy_distribution":"⚡ Energy Distribution",
    "flow_delay":         "⏱ Flow Delay",
    "summary_dashboard":  "📋 Summary Dashboard",
    "compare_pdr":        "🔀 Compare PDR",
    "compare_battery":    "🔀 Compare Battery",
    "compare_throughput": "🔀 Compare Throughput",
}


class GraphsPanel(ctk.CTkFrame):
    """Graph viewer with sidebar selector and embedded image display."""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._graphs_dir  = None
        self._graph_paths = {}
        self._current_key = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left sidebar — graph list
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                               corner_radius=0, width=200)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(sidebar, text="Graphs",
                     font=FONTS["subhead"],
                     text_color=COLORS["accent"]).pack(padx=14, pady=(16, 8), anchor="w")

        self._btn_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent",
            scrollbar_button_color=COLORS["accent_dim"]
        )
        self._btn_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self._graph_buttons = {}

        # Main view area
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(main, fg_color=COLORS["bg_card"],
                               corner_radius=0, height=44)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        self._title_lbl = ctk.CTkLabel(
            toolbar, text="Select a graph from the list",
            font=FONTS["subhead"], text_color=COLORS["text_secondary"]
        )
        self._title_lbl.pack(side="left", padx=16)

        ctk.CTkButton(
            toolbar, text="⬇ Save PNG",
            width=110, height=28,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            border_width=1, border_color=COLORS["accent"],
            corner_radius=5, font=FONTS["small"],
            command=self._save_current
        ).pack(side="right", padx=12)

        # Image label
        self._img_frame = ctk.CTkFrame(main, fg_color=COLORS["bg_primary"],
                                       corner_radius=0)
        self._img_frame.grid(row=1, column=0, sticky="nsew")
        self._img_frame.grid_rowconfigure(0, weight=1)
        self._img_frame.grid_columnconfigure(0, weight=1)

        self._img_label = ctk.CTkLabel(
            self._img_frame,
            text="No graph available.\nRun a simulation first.",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        )
        self._img_label.grid(row=0, column=0, sticky="nsew")

    def load_graphs(self, graphs_dir: str):
        """Scan a graphs directory and populate the sidebar."""
        self._graphs_dir = Path(graphs_dir)
        self._graph_paths = {}

        # Clear old buttons
        for w in self._btn_frame.winfo_children():
            w.destroy()
        self._graph_buttons = {}

        for png in sorted(self._graphs_dir.glob("*.png")):
            key = png.stem
            label = GRAPH_LABELS.get(key, key.replace("_", " ").title())
            self._graph_paths[key] = str(png)
            btn = ctk.CTkButton(
                self._btn_frame, text=label,
                anchor="w",
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_primary"],
                font=FONTS["small"],
                height=32,
                corner_radius=6,
                command=lambda k=key: self.show_graph(k)
            )
            btn.pack(fill="x", pady=2)
            self._graph_buttons[key] = btn

        # Auto-show first graph
        if self._graph_paths:
            first_key = next(iter(self._graph_paths))
            self.show_graph(first_key)

    def show_graph(self, key: str):
        """Display a graph by key."""
        path = self._graph_paths.get(key)
        if not path or not Path(path).exists():
            return

        # Highlight active button
        for k, btn in self._graph_buttons.items():
            btn.configure(
                fg_color=COLORS["bg_active"] if k == key else "transparent",
                text_color=COLORS["accent"] if k == key else COLORS["text_primary"]
            )

        label = GRAPH_LABELS.get(key, key.replace("_", " ").title())
        self._title_lbl.configure(text=label)
        self._current_key = key

        # Load and display image
        try:
            img = Image.open(path)
            # Scale to fit frame
            fw = self._img_frame.winfo_width() or 900
            fh = self._img_frame.winfo_height() or 600
            img.thumbnail((fw - 20, fh - 20), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                   size=(img.width, img.height))
            self._img_label.configure(image=ctk_img, text="")
            self._img_label._image = ctk_img  # keep reference
        except Exception as e:
            self._img_label.configure(image=None, text=f"Error loading image: {e}")

    def _save_current(self):
        if not self._current_key:
            return
        from tkinter import filedialog
        import shutil
        src = self._graph_paths.get(self._current_key)
        if not src:
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile=f"{self._current_key}.png"
        )
        if dest:
            shutil.copy(src, dest)
