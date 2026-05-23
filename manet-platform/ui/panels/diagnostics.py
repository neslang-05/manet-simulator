"""
ui/panels/diagnostics.py — WSL Diagnostics Panel
"""

import customtkinter as ctk
import threading
from tkinter import messagebox
from ui.theme import COLORS, FONTS, RADIUS
from backend.wsl_bridge import WSLBridge
from backend.paths import get_resource_path


DIAG_ITEMS = [
    ("wsl",         "WSL 2 Connected"),
    ("build_tools", "WSL Build Tools"),
    ("ns3",         "NS-3 Available"),
    ("netanim",     "NetAnim Available"),
    ("sim",         "manet-sim.cc Installed"),
]


class DiagnosticsPanel(ctk.CTkFrame):
    """WSL environment diagnostics panel."""

    def __init__(self, parent, console=None, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_secondary"])
        super().__init__(parent, **kwargs)
        import queue
        self._gui_queue = queue.Queue()
        self._process_gui_queue()
        self._bridge  = WSLBridge()
        self._console = console
        self._status  = {}
        self._build_ui()
        self.safe_after(500, self.run_diagnostics)

    def _process_gui_queue(self):
        import queue
        try:
            while True:
                callback = self._gui_queue.get_nowait()
                try:
                    callback()
                except Exception as e:
                    print(f"[DiagnosticsPanel] Error executing GUI callback: {e}")
                self._gui_queue.task_done()
        except queue.Empty:
            pass
        self.after(20, self._process_gui_queue)

    def safe_after(self, delay, callback, *args):
        """Thread-safe version of after()."""
        import threading
        if threading.current_thread() is threading.main_thread():
            return self.after(delay, callback, *args)
        else:
            if delay == 0:
                self._gui_queue.put(lambda: callback(*args))
            else:
                self._gui_queue.put(lambda: self.after(delay, callback, *args))

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
            text_color="#FFFFFF", corner_radius=RADIUS["sm"],
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
            self.safe_after(0, lambda: self._set_status("wsl", ok, msg))

            ok, missing = self._bridge.check_build_tools()
            msg = "All build tools found" if ok else f"Missing: {', '.join(missing)}"
            self.safe_after(0, lambda: self._set_status("build_tools", ok, msg))

            ok, msg = self._bridge.check_ns3()
            self.safe_after(0, lambda: self._set_status("ns3", ok, msg))

            ok, msg = self._bridge.check_netanim()
            self.safe_after(0, lambda: self._set_status("netanim", ok, msg))

            ok, msg = self._bridge.check_sim_installed()
            self.safe_after(0, lambda: self._set_status("sim", ok, msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _prompt_user(self, title: str, message: str) -> bool:
        """Show a confirmation dialog on the main thread and block the background thread until answered."""
        event = threading.Event()
        result = [False]

        def ask():
            res = messagebox.askyesno(title, message)
            result[0] = res
            event.set()

        self.safe_after(0, ask)
        event.wait()
        return result[0]

    def _run_async_wsl_step(self, method_name: str, *args) -> bool:
        """Run an async WSL bridge installation method and block until finished, streaming output to log."""
        event = threading.Event()
        success = [False]

        def on_out(line):
            self.safe_after(0, lambda: self._append_log(line))

        def on_done(rc):
            success[0] = (rc == 0)
            event.set()

        # Retrieve and call the method from the bridge
        method = getattr(self._bridge, method_name)
        
        # Invoke the bridge method.
        self.safe_after(0, lambda: method(*args, on_out, on_done))
        
        event.wait()
        return success[0]

    def _finish_wizard(self, success: bool):
        self._installing = False
        if success:
            self.safe_after(0, lambda: messagebox.showinfo("Success", "All dependencies, files, and simulation binaries have been successfully set up! You are ready to run simulations."))
        else:
            self.safe_after(0, lambda: messagebox.showwarning("Incomplete", "The setup wizard did not complete successfully. Please review the log for errors."))
        self.safe_after(0, self.run_diagnostics)

    def _do_install(self):
        import os
        from pathlib import Path
        
        # Prevent double-clicking/running simultaneously
        if getattr(self, "_installing", False):
            messagebox.showinfo("Installation in Progress", "An installation process is already running. Please check the log below.")
            return
        
        self._installing = True
        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")
        
        self._append_log("=== Starting Automated Dependency Setup Wizard ===")
        
        def run_wizard():
            # Step 1: Check WSL
            self._append_log("[Wizard] Checking WSL connectivity...")
            ok, msg = self._bridge.check_wsl()
            if not ok:
                self.safe_after(0, lambda: messagebox.showerror("WSL Missing", f"WSL 2 is not connected or not available.\nError: {msg}\n\nPlease install WSL2 and Ubuntu manually."))
                self._finish_wizard(False)
                return
            self._append_log("[Wizard] WSL is available.")

            # Step 2: Check Build Tools
            self._append_log("[Wizard] Checking WSL build tools (g++, cmake, ninja, git, qmake)...")
            ok, missing = self._bridge.check_build_tools()
            if not ok:
                self._append_log(f"[Wizard] Missing build tools: {', '.join(missing)}")
                response = self._prompt_user(
                    "Install Build Tools",
                    f"The following WSL packages/build tools are missing:\n{', '.join(missing)}\n\n"
                    f"Would you like to install them automatically now?\n"
                    f"(Requires internet access and root privileges via 'wsl -u root')"
                )
                if not response:
                    self._append_log("[Wizard] User declined build tools installation. Aborting.")
                    self._finish_wizard(False)
                    return
                
                self._append_log("[Wizard] Installing build tools and library dependencies...")
                success = self._run_async_wsl_step("install_wsl_dependencies")
                if not success:
                    self._append_log("[Wizard] Build tools installation failed. Aborting.")
                    self._finish_wizard(False)
                    return
                self._append_log("[Wizard] Build tools and dependencies installed successfully.")
            else:
                self._append_log("[Wizard] All required build tools are already installed.")

            # Step 3: Check NS-3
            self._append_log("[Wizard] Checking NS-3 installation...")
            ok, _ = self._bridge.check_ns3()
            if not ok:
                response = self._prompt_user(
                    "Install NS-3",
                    "NS-3 is not installed at ~/ns-3-dev inside WSL.\n\n"
                    "Would you like the wizard to clone and compile NS-3 now?\n"
                    "(Warning: Building NS-3 takes 15-40 minutes depending on your CPU)"
                )
                if not response:
                    self._append_log("[Wizard] User declined NS-3 installation. Aborting.")
                    self._finish_wizard(False)
                    return
                
                self._append_log("[Wizard] Cloning and building NS-3 (this will take a while)...")
                success = self._run_async_wsl_step("install_ns3")
                if not success:
                    self._append_log("[Wizard] NS-3 compilation failed. Aborting.")
                    self._finish_wizard(False)
                    return
                self._append_log("[Wizard] NS-3 installed successfully.")
            else:
                self._append_log("[Wizard] NS-3 is already installed.")

            # Step 4: Check NetAnim
            self._append_log("[Wizard] Checking NetAnim installation...")
            ok, _ = self._bridge.check_netanim()
            if not ok:
                response = self._prompt_user(
                    "Install NetAnim",
                    "NetAnim is not installed at ~/netanim/build/netanim inside WSL.\n\n"
                    "Would you like the wizard to clone and compile NetAnim now?"
                )
                if not response:
                    self._append_log("[Wizard] User declined NetAnim installation. Aborting.")
                    self._finish_wizard(False)
                    return
                
                self._append_log("[Wizard] Cloning and building NetAnim...")
                success = self._run_async_wsl_step("install_netanim")
                if not success:
                    self._append_log("[Wizard] NetAnim compilation failed. Aborting.")
                    self._finish_wizard(False)
                    return
                self._append_log("[Wizard] NetAnim installed successfully.")
            else:
                self._append_log("[Wizard] NetAnim is already installed.")

            # Step 5: Install/compile simulation scratch files
            self._append_log("[Wizard] Copying simulation files into scratch and compiling targets...")
            cc_path = str(get_resource_path("ns3", "manet-sim.cc"))
            success = self._run_async_wsl_step("install_sim", cc_path)
            if not success:
                self._append_log("[Wizard] Compilation of simulation files failed. Aborting.")
                self._finish_wizard(False)
                return
            
            self._append_log("[Wizard] === Setup completed successfully! ===")
            self._finish_wizard(True)

        threading.Thread(target=run_wizard, daemon=True).start()

    def _show_ns3_version(self):
        def _worker():
            ok, out = self._bridge.run_sync(
                f"cd ~/ns-3-dev && ./ns3 --version 2>&1"
            )
            self.safe_after(0, lambda: self._append_log(out))
        threading.Thread(target=_worker, daemon=True).start()

    def get_status(self) -> dict:
        return dict(self._status)
