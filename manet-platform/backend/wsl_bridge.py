"""
wsl_bridge.py — WSL Integration Layer
Handles all WSL subprocess execution, detection, and file path translation.
"""

import subprocess
import os
import threading
import shlex
from pathlib import Path
from typing import Callable, Optional


class WSLBridge:
    """Bridge between Windows Python and WSL Ubuntu for NS-3 execution."""

    NS3_DIR  = "~/ns-3-dev"
    NETANIM  = "~/netanim/build/netanim"
    SCRATCH  = "~/ns-3-dev/scratch"

    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._cancel_flag = threading.Event()

    # ── Detection ──────────────────────────────────────────────────────
    def check_wsl(self) -> tuple[bool, str]:
        """Check if WSL is available."""
        try:
            r = subprocess.run(
                ["wsl", "--status"],
                capture_output=True, text=True, timeout=10
            )
            return True, "WSL is available"
        except FileNotFoundError:
            return False, "WSL not found in PATH"
        except subprocess.TimeoutExpired:
            return False, "WSL did not respond in time"
        except Exception as e:
            return False, str(e)

    def check_build_tools(self) -> tuple[bool, list[str]]:
        """Check if required build tools (g++, cmake, ninja, git, qmake) are installed in WSL."""
        missing = []
        for cmd in ["g++", "cmake", "ninja", "git"]:
            ok, _ = self.run_sync(f"which {cmd}")
            if not ok:
                missing.append(cmd)
        ok, _ = self.run_sync("which qmake || which qmake-qt5")
        if not ok:
            missing.append("qmake (Qt5)")
        return len(missing) == 0, missing

    def check_ns3(self) -> tuple[bool, str]:
        """Check if ns-3-dev exists inside WSL."""
        ok, out = self.run_sync(f"test -d {self.NS3_DIR} && echo OK || echo NOTFOUND")
        if ok and "OK" in out:
            return True, f"NS-3 found at {self.NS3_DIR}"
        return False, f"NS-3 not found at {self.NS3_DIR}"

    def check_netanim(self) -> tuple[bool, str]:
        """Check if NetAnim binary exists inside WSL."""
        ok, out = self.run_sync(f"test -f {self.NETANIM} && echo OK || echo NOTFOUND")
        if ok and "OK" in out:
            return True, f"NetAnim found at {self.NETANIM}"
        return False, f"NetAnim not found at {self.NETANIM}"

    def check_sim_installed(self) -> tuple[bool, str]:
        """Check if manet-sim.cc is in scratch."""
        ok, out = self.run_sync(
            f"test -f {self.SCRATCH}/manet-sim.cc && echo OK || echo NOTFOUND"
        )
        if ok and "OK" in out:
            return True, "manet-sim.cc is installed"
        return False, "manet-sim.cc not installed (use Install button)"

    def get_wsl_username(self) -> str:
        """Get the WSL default username."""
        _, out = self.run_sync("whoami")
        return out.strip()

    # ── Synchronous helper ─────────────────────────────────────────────
    def run_sync(self, cmd: str, timeout: int = 30) -> tuple[bool, str]:
        """Run a WSL command synchronously and return (success, output)."""
        try:
            r = subprocess.run(
                ["wsl", "bash", "-c", cmd],
                capture_output=True, text=True, timeout=timeout
            )
            combined = r.stdout + r.stderr
            return r.returncode == 0, combined.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    # ── Async streaming execution ──────────────────────────────────────
    def run_async(
        self,
        wsl_cmd: str,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Run a WSL command asynchronously, streaming output line-by-line."""
        self._cancel_flag.clear()

        def _worker():
            try:
                self._process = subprocess.Popen(
                    ["wsl", "bash", "-c", wsl_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in self._process.stdout:
                    if self._cancel_flag.is_set():
                        self._process.terminate()
                        on_output("[CANCELLED] Simulation cancelled by user.")
                        on_done(-1)
                        return
                    on_output(line.rstrip())
                self._process.wait()
                on_done(self._process.returncode)
            except Exception as e:
                on_output(f"[ERROR] {e}")
                on_done(-1)
            finally:
                self._process = None

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def run_async_root(
        self,
        wsl_cmd: str,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Run a WSL command asynchronously as root (passwordless via 'wsl -u root')."""
        self._cancel_flag.clear()

        def _worker():
            try:
                self._process = subprocess.Popen(
                    ["wsl", "-u", "root", "bash", "-c", wsl_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in self._process.stdout:
                    if self._cancel_flag.is_set():
                        self._process.terminate()
                        on_output("[CANCELLED] Command cancelled by user.")
                        on_done(-1)
                        return
                    on_output(line.rstrip())
                self._process.wait()
                on_done(self._process.returncode)
            except Exception as e:
                on_output(f"[ERROR] {e}")
                on_done(-1)
            finally:
                self._process = None

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def cancel(self):
        """Cancel the currently running simulation."""
        self._cancel_flag.set()
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    # ── File operations ────────────────────────────────────────────────
    def install_sim(self, cc_path_windows: str, on_output: Callable[[str], None],
                    on_done: Callable[[int], None]) -> None:
        """Run install.sh to copy all simulation files into WSL scratch and build them.

        install.sh copies:
          - manet-sim.cc    (unified GUI simulation)
          - lab-aodv.cc     (AODV example)
          - dsdv-manet.cc   (DSDV example)
          - lab-dsr.cc      (DSR  example)
          - lab-olsr.cc     (OLSR example)
          - CMakeLists.txt  (links ns3-netanim for all targets)
        """
        # Derive the ns3/ folder from the cc_path_windows (e.g. .../ns3/manet-sim.cc)
        ns3_folder_win = str(Path(cc_path_windows).parent)
        ns3_folder_wsl = self._win_to_wsl(ns3_folder_win)
        install_script = f"{ns3_folder_wsl}/install.sh"

        cmd = (
            f"chmod +x '{install_script}' && "
            f"bash '{install_script}' 2>&1"
        )
        on_output("[WSL] Running install.sh — copying all simulation files and building...")
        self.run_async(cmd, on_output, on_done)

    def install_wsl_dependencies(
        self,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Install required WSL compiler and library dependencies as root."""
        # Install build dependencies required for NS-3 and NetAnim.
        # This handles both Ubuntu 20.04 and 22.04 by installing qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5svg5-dev
        packages = (
            "g++ python3 python3-pip cmake ninja-build git "
            "libsqlite3-dev libxml2-dev libgtk-3-dev "
            "libboost-all-dev mercurial gsl-bin libgsl-dev "
            "qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5svg5-dev"
        )
        cmd = f"apt-get update && apt-get install -y {packages} 2>&1"
        self.run_async_root(cmd, on_output, on_done)

    def install_ns3(
        self,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Clone and build NS-3 in WSL."""
        cmd = (
            f"cd ~ && "
            f"if [ ! -d '{self.NS3_DIR}' ]; then "
            f"  git clone https://gitlab.com/nsnam/ns-3-dev.git {self.NS3_DIR} 2>&1; "
            f"fi && "
            f"cd {self.NS3_DIR} && "
            f"./ns3 configure --enable-examples --enable-tests 2>&1 && "
            f"./ns3 build 2>&1"
        )
        self.run_async(cmd, on_output, on_done)

    def install_netanim(
        self,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Clone and build NetAnim in WSL."""
        cmd = (
            f"cd ~ && "
            f"if [ ! -d '~/netanim' ]; then "
            f"  git clone https://gitlab.com/nsnam/netanim.git ~/netanim 2>&1; "
            f"fi && "
            f"cd ~/netanim && "
            f"qmake NetAnim.pro 2>&1 && "
            f"make -j$(nproc) 2>&1"
        )
        self.run_async(cmd, on_output, on_done)

    def _win_to_wsl(self, win_path: str) -> str:
        """Convert a Windows path to WSL /mnt/... path."""
        p = Path(win_path)
        parts = p.parts
        # e.g. D:\foo\bar -> /mnt/d/foo/bar
        drive = parts[0].replace(':', '').replace('\\', '').lower()
        rest  = '/'.join(parts[1:])
        return f"/mnt/{drive}/{rest}"

    def wsl_path_to_windows(self, wsl_path: str) -> str:
        """Translate WSL path to UNC Windows path."""
        # e.g. /home/user/... -> \\wsl$\Ubuntu\home\user\...
        ok, distro = self.run_sync("echo $WSL_DISTRO_NAME")
        distro = distro.replace('\x00', '').strip() or "Ubuntu"
        clean = wsl_path.replace('\x00', '').lstrip('/')
        win_sep = '\\'
        clean_win = clean.replace('/', win_sep)
        return f"\\\\wsl$\\{distro}\\{clean_win}"

    # ── Simulation execution ───────────────────────────────────────────
    def run_simulation(
        self,
        params: dict,
        output_dir_wsl: str,
        on_output: Callable[[str], None],
        on_done: Callable[[int], None]
    ) -> None:
        """Build the NS-3 run command and execute it asynchronously."""
        args = " ".join([
            f"--protocol={params['protocol']}",
            f"--numNodes={params['numNodes']}",
            f"--simTime={params['simTime']}",
            f"--battery={params['battery']}",
            f"--areaWidth={params['areaWidth']}",
            f"--areaHeight={params['areaHeight']}",
            f"--speed={params['speed']}",
            f"--pauseTime={params['pauseTime']}",
            f"--packetSize={params['packetSize']}",
            f"--dataRate={params['dataRate']}",
            f"--txRange={params['txRange']}",
            f"--outputDir={output_dir_wsl}",
        ])
        cmd = (
            f"mkdir -p {output_dir_wsl} && "
            f"cd {self.NS3_DIR} && "
            f"./ns3 run 'manet-sim {args}' 2>&1"
        )
        on_output(f"[WSL] Running: {cmd}")
        self.run_async(cmd, on_output, on_done)

    def launch_netanim(self, xml_wsl_path: str) -> None:
        """Launch NetAnim with the given XML file (non-blocking)."""
        cmd = f"{self.NETANIM} {xml_wsl_path}"
        subprocess.Popen(["wsl", "bash", "-c", cmd])
