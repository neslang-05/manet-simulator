# =============================================================================
# CMakeLists.txt — NS-3 Scratch Build for MANET Simulator
#
# Place this file inside ~/ns-3-dev/scratch/  (the install.sh does this
# automatically when you click "Install & Build" in the Diagnostics panel).
#
# All four protocol examples + the unified manet-sim are built here.
# Each executable links against ns3-netanim so NetAnim XML output works.
# =============================================================================

cmake_minimum_required(VERSION 3.10)

# ── Unified simulation (used by the Python GUI) ───────────────────────────────
build_exec(
  FILENAME manet-sim.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libinternet}
    ${libmobility}
    ${libwifi}
    ${libaodv}
    ${libdsdv}
    ${libdsr}
    ${libolsr}
    ${libapplications}
    ${libflow-monitor}
    ${libenergy}
    ${libnetanim}            # ← NetAnim library
)

# ── AODV stand-alone example ──────────────────────────────────────────────────
build_exec(
  FILENAME lab-aodv.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libinternet}
    ${libmobility}
    ${libwifi}
    ${libaodv}
    ${libapplications}
    ${libflow-monitor}
    ${libenergy}
    ${libnetanim}            # ← NetAnim library
)

# ── DSDV stand-alone example ──────────────────────────────────────────────────
build_exec(
  FILENAME dsdv-manet.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libinternet}
    ${libmobility}
    ${libwifi}
    ${libdsdv}
    ${libapplications}
    ${libflow-monitor}
    ${libenergy}
    ${libnetanim}            # ← NetAnim library
)

# ── DSR stand-alone example ───────────────────────────────────────────────────
build_exec(
  FILENAME lab-dsr.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libinternet}
    ${libmobility}
    ${libwifi}
    ${libdsr}
    ${libapplications}
    ${libflow-monitor}
    ${libenergy}
    ${libnetanim}            # ← NetAnim library
)

# ── OLSR stand-alone example ──────────────────────────────────────────────────
build_exec(
  FILENAME lab-olsr.cc
  LIBRARIES_TO_LINK
    ${libcore}
    ${libnetwork}
    ${libinternet}
    ${libmobility}
    ${libwifi}
    ${libolsr}
    ${libapplications}
    ${libflow-monitor}
    ${libenergy}
    ${libnetanim}            # ← NetAnim library
)
