/* =================================================================
 * lab-olsr.cc — OLSR MANET Simulation (NS-3)
 * Protocol  : OLSR (Optimized Link State Routing)
 * Features  : Mobility, Energy model, FlowMonitor, NetAnim animation
 * Output    : olsr-animation.xml  (open in NetAnim for visualization)
 * ================================================================= */

#include <fstream>
#include <iostream>
#include <string>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/olsr-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/energy-module.h"
#include "ns3/netanim-module.h"       // ← NetAnim header

using namespace ns3;
using namespace ns3::energy;

NS_LOG_COMPONENT_DEFINE("LabOlsr");

// ── Packet counters ────────────────────────────────────────────────
static uint64_t g_tx = 0;
static uint64_t g_rx = 0;
void TxTrace(Ptr<const Packet>) { g_tx++; }
void RxTrace(Ptr<const Packet>, const Address &) { g_rx++; }

int main(int argc, char *argv[])
{
    // ── Parameters ─────────────────────────────────────────────────
    uint32_t    nNodes      = 20;
    double      simTime     = 60.0;
    double      areaX       = 1000.0;
    double      areaY       = 1000.0;
    double      speed       = 10.0;
    double      pauseTime   = 2.0;
    double      battery     = 100.0;
    double      txRange     = 250.0;
    uint32_t    packetSize  = 512;
    std::string dataRate    = "2Mbps";
    std::string animFile    = "olsr-animation.xml";

    CommandLine cmd(__FILE__);
    cmd.AddValue("nNodes",     "Number of nodes",            nNodes);
    cmd.AddValue("simTime",    "Simulation time (s)",        simTime);
    cmd.AddValue("areaX",      "Area width (m)",             areaX);
    cmd.AddValue("areaY",      "Area height (m)",            areaY);
    cmd.AddValue("speed",      "Max node speed (m/s)",       speed);
    cmd.AddValue("pauseTime",  "Pause time (s)",             pauseTime);
    cmd.AddValue("battery",    "Battery capacity (J)",       battery);
    cmd.AddValue("txRange",    "TX range (m)",               txRange);
    cmd.AddValue("packetSize", "Packet size (bytes)",        packetSize);
    cmd.AddValue("dataRate",   "Data rate (e.g. 2Mbps)",    dataRate);
    cmd.AddValue("animFile",   "NetAnim output XML file",   animFile);
    cmd.Parse(argc, argv);

    NS_LOG_INFO("[OLSR] Nodes=" << nNodes << " SimTime=" << simTime
                << " Area=" << areaX << "x" << areaY);

    // ── Nodes ──────────────────────────────────────────────────────
    NodeContainer nodes;
    nodes.Create(nNodes);

    // ── WiFi ───────────────────────────────────────────────────────
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                  "DataMode",    StringValue("DsssRate2Mbps"),
                                  "ControlMode", StringValue("DsssRate1Mbps"));

    YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
    wifiChannel.AddPropagationLoss("ns3::RangePropagationLossModel",
                                    "MaxRange", DoubleValue(txRange));

    YansWifiPhyHelper wifiPhy;
    wifiPhy.SetChannel(wifiChannel.Create());

    WifiMacHelper wifiMac;
    wifiMac.SetType("ns3::AdhocWifiMac");

    NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, nodes);

    // ── Energy ─────────────────────────────────────────────────────
    BasicEnergySourceHelper energyHelper;
    energyHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(battery));
    EnergySourceContainer sources = energyHelper.Install(nodes);

    WifiRadioEnergyModelHelper radioEnergy;
    radioEnergy.Install(devices, sources);

    // ── Mobility ───────────────────────────────────────────────────
    MobilityHelper mobility;
    mobility.SetPositionAllocator(
        "ns3::RandomRectanglePositionAllocator",
        "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=" + std::to_string(areaX) + "]"),
        "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=" + std::to_string(areaY) + "]"));
    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed",  StringValue("ns3::UniformRandomVariable[Min=1.0|Max=" + std::to_string(speed) + "]"),
        "Pause",  StringValue("ns3::ConstantRandomVariable[Constant=" + std::to_string(pauseTime) + "]"),
        "PositionAllocator", PointerValue(CreateObject<RandomRectanglePositionAllocator>()));
    mobility.Install(nodes);

    // ── OLSR Routing ───────────────────────────────────────────────
    OlsrHelper olsr;
    InternetStackHelper internet;
    internet.SetRoutingHelper(olsr);
    internet.Install(nodes);

    Ipv4AddressHelper ipv4;
    ipv4.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer ifaces = ipv4.Assign(devices);

    // ── UDP CBR Traffic ────────────────────────────────────────────
    uint16_t  port      = 9;
    uint32_t  sinkCount = std::max(1u, nNodes / 4);

    PacketSinkHelper sink("ns3::UdpSocketFactory",
                           InetSocketAddress(Ipv4Address::GetAny(), port));
    ApplicationContainer sinkApps;
    for (uint32_t i = 0; i < sinkCount; i++)
        sinkApps.Add(sink.Install(nodes.Get(i)));
    sinkApps.Start(Seconds(1.0));
    sinkApps.Stop(Seconds(simTime));

    for (uint32_t i = 0; i < sinkCount; i++)
        sinkApps.Get(i)->TraceConnectWithoutContext("Rx", MakeCallback(&RxTrace));

    double startOff = 2.0;
    for (uint32_t i = sinkCount; i < nNodes; i++)
    {
        uint32_t dst = i % sinkCount;
        OnOffHelper onoff("ns3::UdpSocketFactory",
            InetSocketAddress(ifaces.GetAddress(dst), port));
        onoff.SetConstantRate(DataRate(dataRate), packetSize);
        ApplicationContainer srcApp = onoff.Install(nodes.Get(i));
        srcApp.Start(Seconds(startOff));
        srcApp.Stop(Seconds(simTime - 1.0));
        srcApp.Get(0)->TraceConnectWithoutContext("Tx", MakeCallback(&TxTrace));
        startOff += 0.1;
        if (startOff > simTime / 2) startOff = 2.0;
    }

    // ── FlowMonitor ────────────────────────────────────────────────
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    // ── NetAnim ────────────────────────────────────────────────────
    // Creates the XML animation file to be opened in NetAnim GUI
    AnimationInterface anim(animFile);
    anim.SetMaxPktsPerTraceFile(500000);
    for (uint32_t i = 0; i < nNodes; i++)
    {
        anim.UpdateNodeDescription(nodes.Get(i), "OLSR-" + std::to_string(i));
        // Red/crimson colour to identify OLSR nodes
        anim.UpdateNodeColor(nodes.Get(i), 204, 0, 51);
    }

    // ── Run ────────────────────────────────────────────────────────
    Simulator::Stop(Seconds(simTime));
    Simulator::Run();

    // ── FlowMonitor stats ──────────────────────────────────────────
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier =
        DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats();

    double totalTp = 0, totalDelay = 0;
    uint32_t flowCount = 0;
    for (auto &kv : stats)
    {
        if (kv.second.rxPackets > 0)
        {
            double tp = kv.second.rxBytes * 8.0 /
                (kv.second.timeLastRxPacket.GetSeconds() -
                 kv.second.timeFirstTxPacket.GetSeconds()) / 1000.0;
            double delay = kv.second.delaySum.GetMilliSeconds() / kv.second.rxPackets;
            totalTp    += tp;
            totalDelay += delay;
            flowCount++;
        }
    }

    double pdr = (g_tx > 0) ? (100.0 * g_rx / g_tx) : 0.0;

    std::cout << "\n[OLSR] ===== Simulation Results =====" << std::endl;
    std::cout << "[OLSR] TX Packets   : " << g_tx       << std::endl;
    std::cout << "[OLSR] RX Packets   : " << g_rx       << std::endl;
    std::cout << "[OLSR] PDR          : " << pdr        << " %" << std::endl;
    std::cout << "[OLSR] Avg Throughput: "
              << (flowCount > 0 ? totalTp / flowCount : 0) << " kbps" << std::endl;
    std::cout << "[OLSR] Avg Delay    : "
              << (flowCount > 0 ? totalDelay / flowCount : 0) << " ms" << std::endl;
    std::cout << "[OLSR] Animation    : " << animFile   << std::endl;
    std::cout << "[OLSR] ====================================\n" << std::endl;

    Simulator::Destroy();
    return 0;
}
