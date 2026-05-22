"""
ui/panels/graphs.py — Graph Viewer Panel
Embeds Matplotlib figures inside the CustomTkinter UI.
Supports interactive zoom controls: +/−/reset buttons, scroll-wheel, and
a live zoom percentage label in the toolbar.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
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

# Zoom configuration
_ZOOM_STEP   = 0.15   # zoom-in/out increment per click / scroll tick
_ZOOM_MIN    = 0.25   # minimum zoom level (25%)
_ZOOM_MAX    = 5.00   # maximum zoom level (500%)
_ZOOM_DEFAULT = 1.0   # default zoom level (100%)


class GraphsPanel(ctk.CTkFrame):
    """Graph viewer with sidebar selector, embedded image display, and zoom controls."""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        self._graphs_dir  = None
        self._graph_paths = {}
        self._current_key = None
        self._zoom_level  = _ZOOM_DEFAULT   # current zoom multiplier
        self._orig_image  = None            # original PIL Image for the active graph
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left sidebar — graph list ──────────────────────────────────────────
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

        # ── Main view area ─────────────────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # ── Toolbar ────────────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(main, fg_color=COLORS["bg_card"],
                               corner_radius=0, height=44)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)

        # Graph title (left side)
        self._title_lbl = ctk.CTkLabel(
            toolbar, text="Select a graph from the list",
            font=FONTS["subhead"], text_color=COLORS["text_secondary"]
        )
        self._title_lbl.pack(side="left", padx=16)

        # Save button (right side)
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

        # ── Zoom controls (right of toolbar, left of Save button) ──────────────
        zoom_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        zoom_frame.pack(side="right", padx=(0, 6))

        _btn_style = dict(
            width=30, height=28,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=5, font=FONTS["small"],
        )

        ctk.CTkButton(
            zoom_frame, text="−",
            command=self._zoom_out,
            **_btn_style
        ).pack(side="left", padx=2)

        self._zoom_lbl = ctk.CTkLabel(
            zoom_frame, text="100%",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            width=44,
        )
        self._zoom_lbl.pack(side="left", padx=2)

        ctk.CTkButton(
            zoom_frame, text="+",
            command=self._zoom_in,
            **_btn_style
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            zoom_frame, text="↺",
            command=self._zoom_reset,
            **_btn_style
        ).pack(side="left", padx=(4, 2))

        # ── Scrollable image area ──────────────────────────────────────────────
        # We use a canvas + scrollbars so the image can be panned when zoomed in.
        import tkinter as tk

        canvas_frame = ctk.CTkFrame(main, fg_color=COLORS["bg_primary"], corner_radius=0)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            canvas_frame,
            bg=COLORS["bg_primary"],
            highlightthickness=0,
            bd=0,
        )
        self._canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = ctk.CTkScrollbar(canvas_frame, orientation="vertical",
                                    command=self._canvas.yview,
                                    button_color=COLORS["accent_dim"],
                                    button_hover_color=COLORS["accent"])
        v_scroll.grid(row=0, column=1, sticky="ns")

        h_scroll = ctk.CTkScrollbar(canvas_frame, orientation="horizontal",
                                    command=self._canvas.xview,
                                    button_color=COLORS["accent_dim"],
                                    button_hover_color=COLORS["accent"])
        h_scroll.grid(row=1, column=0, sticky="ew")

        self._canvas.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )

        # Placeholder label drawn on the canvas
        self._canvas_image_id = None
        self._placeholder_id  = self._canvas.create_text(
            400, 300,
            text=(
                "No graph available.\n"
                "Run a new simulation, or\n"
                "load a previous one from the History tab."
            ),
            font=FONTS["body"],
            fill=COLORS["text_muted"],
            justify="center",
        )

        # Keep a reference to the CTkImage so it isn't GC'd
        self._ctk_image_ref = None

        # Bind mouse-wheel zoom
        self._canvas.bind("<MouseWheel>",      self._on_mousewheel)          # Windows
        self._canvas.bind("<Button-4>",        self._on_mousewheel)          # Linux scroll up
        self._canvas.bind("<Button-5>",        self._on_mousewheel)          # Linux scroll down

        # Bind canvas resize so the displayed image scales correctly
        self._canvas.bind("<Configure>", self._on_canvas_resize)

    # ── Graph loading ──────────────────────────────────────────────────────────

    def load_graphs(self, graphs_dir: str):
        """Scan a graphs directory and populate the sidebar."""
        self._graphs_dir = Path(graphs_dir)
        self._graph_paths = {}

        # Clear old buttons
        for w in self._btn_frame.winfo_children():
            w.destroy()
        self._graph_buttons = {}

        for png in sorted(self._graphs_dir.glob("*.png")):
            key   = png.stem
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
        """Display a graph by key (preserves current zoom level)."""
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

        # Load the original image (no scaling yet)
        try:
            self._orig_image = Image.open(path)
            self._orig_image.load()   # force decode so we can close the file handle
        except Exception as e:
            self._canvas.delete("all")
            self._canvas.create_text(
                400, 300, text=f"Error loading image:\n{e}",
                font=FONTS["body"], fill=COLORS["danger"], justify="center"
            )
            return

        # Remove placeholder
        if self._placeholder_id:
            self._canvas.delete(self._placeholder_id)
            self._placeholder_id = None

        self._render_image()

    # ── Rendering helpers ──────────────────────────────────────────────────────

    def _render_image(self):
        """Render the current original image at the current zoom level onto the canvas."""
        if self._orig_image is None:
            return

        orig_w, orig_h = self._orig_image.size
        new_w = max(1, int(orig_w * self._zoom_level))
        new_h = max(1, int(orig_h * self._zoom_level))

        resized = self._orig_image.resize((new_w, new_h), Image.LANCZOS)

        photo_img = ImageTk.PhotoImage(resized)
        self._ctk_image_ref = photo_img   # keep reference

        # Update or create image item on the canvas
        if self._canvas_image_id is not None:
            self._canvas.delete(self._canvas_image_id)

        self._canvas_image_id = self._canvas.create_image(
            0, 0, anchor="nw", image=photo_img
        )
        self._canvas.configure(scrollregion=(0, 0, new_w, new_h))

        # Update zoom label
        self._zoom_lbl.configure(text=f"{int(self._zoom_level * 100)}%")

    def _on_canvas_resize(self, event):
        """When the canvas is resized and zoom is at 1.0, re-fit to frame."""
        # Only auto-fit when at the default zoom so we don't fight the user.
        if abs(self._zoom_level - _ZOOM_DEFAULT) < 0.01 and self._orig_image is not None:
            self._fit_to_frame()

    def _fit_to_frame(self):
        """Compute a zoom level that fits the image inside the canvas."""
        if self._orig_image is None:
            return
        cw = self._canvas.winfo_width()  or 900
        ch = self._canvas.winfo_height() or 600
        orig_w, orig_h = self._orig_image.size
        scale = min(cw / orig_w, ch / orig_h, 1.0)   # never upscale beyond 1× by default
        self._zoom_level = round(scale, 4)
        self._render_image()

    # ── Zoom actions ───────────────────────────────────────────────────────────

    def _zoom_in(self):
        self._zoom_level = min(_ZOOM_MAX, self._zoom_level + _ZOOM_STEP)
        self._render_image()

    def _zoom_out(self):
        self._zoom_level = max(_ZOOM_MIN, self._zoom_level - _ZOOM_STEP)
        self._render_image()

    def _zoom_reset(self):
        """Reset zoom and re-fit image to the canvas."""
        self._zoom_level = _ZOOM_DEFAULT
        if self._orig_image is not None:
            self._fit_to_frame()
        else:
            self._zoom_lbl.configure(text="100%")

    def _on_mousewheel(self, event):
        """Zoom in/out on Ctrl+scroll; plain scroll pans the canvas."""
        # On Windows event.state & 4 is True when Ctrl is held.
        ctrl_held = (event.state & 4) != 0

        if ctrl_held:
            # Determine scroll direction
            if hasattr(event, "delta"):
                direction = 1 if event.delta > 0 else -1
            else:
                direction = 1 if event.num == 4 else -1

            if direction > 0:
                self._zoom_in()
            else:
                self._zoom_out()
        else:
            # Pass scroll to the canvas for vertical panning
            if hasattr(event, "delta"):
                self._canvas.yview_scroll(-1 * (event.delta // 120), "units")
            elif event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            else:
                self._canvas.yview_scroll(1, "units")

    # ── Save ───────────────────────────────────────────────────────────────────

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
