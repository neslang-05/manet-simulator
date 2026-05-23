# =============================================================================
# CMakeLists.txt — NS-3 Scratch Build for MANET Simulator
#
# Place this file inside ~/ns-3-dev/scratch/  (the install.sh does this
# automatically when you click "Install & Build" in the Diagnostics panel).
#
# All four protocol examples + the unified manet-sim are built here.
# NetAnim is linked only if the netanim module is available.
# =============================================================================

cmake_minimum_required(VERSION 3.10)

# ── Optional NetAnim linkage ──────────────────────────────────────────────────
# libnetanim is only defined when the netanim module was successfully configured.
# Guard every use to avoid "target to build does not exist" errors.
if(DEFINED libnetanim AND NOT "${libnetanim}" STREQUAL "")
  set(NETANIM_LIB ${libnetanim})
  set(NETANIM_DEF "NS3_NETANIM")
else()
  set(NETANIM_LIB "")
  set(NETANIM_DEF "")
  message(STATUS "[manet-sim] NetAnim not available — building without animation support")
endif()

# Pass preprocessor flag to C++ so #ifdef NS3_NETANIM in manet-sim.cc works
if(NETANIM_DEF)
  add_compile_definitions(${NETANIM_DEF})
endif()

# ── Unified simulation (used by the Python GUI) ───────────────────────────────
build_exec(
  EXECNAME manet-sim
  SOURCE_FILES manet-sim.cc
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
    ${NETANIM_LIB}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/
)

# ── AODV stand-alone example ──────────────────────────────────────────────────
build_exec(
  EXECNAME lab-aodv
  SOURCE_FILES lab-aodv.cc
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
    ${NETANIM_LIB}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/
)

# ── DSDV stand-alone example ──────────────────────────────────────────────────
build_exec(
  EXECNAME dsdv-manet
  SOURCE_FILES dsdv-manet.cc
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
    ${NETANIM_LIB}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/
)

# ── DSR stand-alone example ───────────────────────────────────────────────────
build_exec(
  EXECNAME lab-dsr
  SOURCE_FILES lab-dsr.cc
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
    ${NETANIM_LIB}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/
)

# ── OLSR stand-alone example ──────────────────────────────────────────────────
build_exec(
  EXECNAME lab-olsr
  SOURCE_FILES lab-olsr.cc
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
    ${NETANIM_LIB}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/
)
