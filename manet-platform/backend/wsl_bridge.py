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
        """Copy manet-sim.cc into WSL scratch and build it."""
        # Convert Windows path to WSL path
        wsl_path = self._win_to_wsl(cc_path_windows)
        cmd = (
            f"mkdir -p {self.SCRATCH} && "
            f"cp '{wsl_path}' {self.SCRATCH}/manet-sim.cc && "
            f"echo '[WSL] Copied manet-sim.cc' && "
            f"cd {self.NS3_DIR} && "
            f"./ns3 build scratch/manet-sim 2>&1"
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
        ok, distro = self.run_sync("wsl.exe -l -q 2>/dev/null | head -1 || echo Ubuntu")
        distro = distro.strip() or "Ubuntu"
        clean = wsl_path.lstrip('/')
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
            f"./ns3 run 'scratch/manet-sim {args}' 2>&1"
        )
        on_output(f"[WSL] Running: {cmd}")
        self.run_async(cmd, on_output, on_done)

    def launch_netanim(self, xml_wsl_path: str) -> None:
        """Launch NetAnim with the given XML file (non-blocking)."""
        cmd = f"{self.NETANIM} {xml_wsl_path}"
        subprocess.Popen(["wsl", "bash", "-c", cmd])
