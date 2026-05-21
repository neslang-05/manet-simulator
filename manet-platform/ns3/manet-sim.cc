/* =================================================================
 * manet-sim.cc — Unified MANET Simulation (NS-3)
 * Supports: AODV, DSDV, DSR, OLSR
 * Features: Energy, Mobility tracking, FlowMonitor, NetAnim
 * Authors: MANET Research Platform
 * ================================================================= */

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <ctime>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/aodv-module.h"
#include "ns3/dsdv-module.h"
#include "ns3/dsr-module.h"
#include "ns3/olsr-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/energy-module.h"
#include "ns3/netanim-module.h"

using namespace ns3;
using namespace ns3::energy;

NS_LOG_COMPONENT_DEFINE("ManetSim");

// ─── Global CSV streams ────────────────────────────────────────────
std::ofstream g_batteryCsv;
std::ofstream g_mobilityCsv;
std::ofstream g_throughputCsv;

// ─── Globals ───────────────────────────────────────────────────────
static uint32_t g_numNodes     = 20;
static double   g_simTime      = 60.0;
static double   g_areaWidth    = 1000.0;
static double   g_areaHeight   = 1000.0;
static double   g_speed        = 10.0;
static double   g_pauseTime    = 2.0;
static double   g_battery      = 100.0;
static double   g_txRange      = 250.0;
static uint32_t g_packetSize   = 512;
static std::string g_dataRate  = "2Mbps";
static std::string g_protocol  = "AODV";
static std::string g_outputDir = "outputs";

NodeContainer g_nodes;
EnergySourceContainer g_energySources;

// ─── Packet counters ───────────────────────────────────────────────
static uint64_t g_txPackets = 0;
static uint64_t g_rxPackets = 0;

void TxCallback(Ptr<const Packet>) { g_txPackets++; }
void RxCallback(Ptr<const Packet>, const Address &) { g_rxPackets++; }

// ─── Battery monitoring ────────────────────────────────────────────
void LogBattery()
{
    double now = Simulator::Now().GetSeconds();
    for (uint32_t i = 0; i < g_energySources.GetN(); i++)
    {
        Ptr<BasicEnergySource> src =
            DynamicCast<BasicEnergySource>(g_energySources.Get(i));
        if (src)
        {
            g_batteryCsv << now << "," << i << ","
                         << src->GetRemainingEnergy() << "\n";
        }
    }
    g_batteryCsv.flush();
    if (Simulator::Now().GetSeconds() + 1.0 <= g_simTime)
        Simulator::Schedule(Seconds(1.0), &LogBattery);
}

// ─── Mobility monitoring ───────────────────────────────────────────
void LogMobility()
{
    double now = Simulator::Now().GetSeconds();
    for (uint32_t i = 0; i < g_nodes.GetN(); i++)
    {
        Ptr<MobilityModel> mob = g_nodes.Get(i)->GetObject<MobilityModel>();
        if (mob)
        {
            Vector pos = mob->GetPosition();
            g_mobilityCsv << now << "," << i << ","
                          << pos.x << "," << pos.y << "\n";
        }
    }
    g_mobilityCsv.flush();
    if (Simulator::Now().GetSeconds() + 1.0 <= g_simTime)
        Simulator::Schedule(Seconds(1.0), &LogMobility);
}

// ─── Throughput monitoring ─────────────────────────────────────────
void LogThroughput()
{
    double now = Simulator::Now().GetSeconds();
    double pdr  = (g_txPackets > 0)
                  ? (100.0 * g_rxPackets / g_txPackets)
                  : 0.0;
    double tp   = (g_rxPackets * g_packetSize * 8.0) / (now * 1000.0); // kbps
    g_throughputCsv << now << "," << g_txPackets << ","
                    << g_rxPackets << "," << pdr << "," << tp << "\n";
    g_throughputCsv.flush();
    if (now + 1.0 <= g_simTime)
        Simulator::Schedule(Seconds(1.0), &LogThroughput);
}

// ─── Main ──────────────────────────────────────────────────────────
int main(int argc, char *argv[])
{
    // ── Command-line arguments ──────────────────────────────────────
    CommandLine cmd(__FILE__);
    cmd.AddValue("protocol",   "Routing protocol (AODV|DSDV|DSR|OLSR)", g_protocol);
    cmd.AddValue("numNodes",   "Number of MANET nodes",                  g_numNodes);
    cmd.AddValue("simTime",    "Simulation duration (seconds)",           g_simTime);
    cmd.AddValue("battery",    "Initial battery energy (Joules)",         g_battery);
    cmd.AddValue("areaWidth",  "Simulation area width (m)",               g_areaWidth);
    cmd.AddValue("areaHeight", "Simulation area height (m)",              g_areaHeight);
    cmd.AddValue("speed",      "Node max speed (m/s)",                    g_speed);
    cmd.AddValue("pauseTime",  "Node pause time (s)",                     g_pauseTime);
    cmd.AddValue("packetSize", "UDP packet size (bytes)",                  g_packetSize);
    cmd.AddValue("dataRate",   "Data rate (e.g. 2Mbps)",                  g_dataRate);
    cmd.AddValue("txRange",    "WiFi transmission range (m)",             g_txRange);
    cmd.AddValue("outputDir",  "Output directory prefix",                 g_outputDir);
    cmd.Parse(argc, argv);

    NS_LOG_INFO("[ManetSim] Protocol=" << g_protocol
        << " Nodes=" << g_numNodes
        << " SimTime=" << g_simTime
        << " Area=" << g_areaWidth << "x" << g_areaHeight
        << " Battery=" << g_battery << "J");

    // ── Open CSV files ──────────────────────────────────────────────
    g_batteryCsv.open(g_outputDir + "/battery.csv");
    g_batteryCsv << "Time,NodeID,RemainingEnergy\n";

    g_mobilityCsv.open(g_outputDir + "/mobility.csv");
    g_mobilityCsv << "Time,NodeID,X,Y\n";

    g_throughputCsv.open(g_outputDir + "/throughput.csv");
    g_throughputCsv << "Time,TxPackets,RxPackets,PDR,Throughput_kbps\n";

    // ── Create nodes ────────────────────────────────────────────────
    g_nodes.Create(g_numNodes);

    // ── WiFi setup ──────────────────────────────────────────────────
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                  "DataMode",    StringValue("DsssRate2Mbps"),
                                  "ControlMode", StringValue("DsssRate1Mbps"));

    YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
    wifiChannel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    wifiChannel.AddPropagationLoss("ns3::RangePropagationLossModel",
                                    "MaxRange", DoubleValue(g_txRange));

    YansWifiPhyHelper wifiPhy;
    wifiPhy.SetChannel(wifiChannel.Create());

    WifiMacHelper wifiMac;
    wifiMac.SetType("ns3::AdhocWifiMac");

    NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, g_nodes);

    // ── Energy model ────────────────────────────────────────────────
    BasicEnergySourceHelper energyHelper;
    energyHelper.Set("BasicEnergySourceInitialEnergyJ",
                     DoubleValue(g_battery));
    g_energySources = energyHelper.Install(g_nodes);

    WifiRadioEnergyModelHelper radioEnergyHelper;
    radioEnergyHelper.Install(devices, g_energySources);

    // ── Mobility ─────────────────────────────────────────────────────
    MobilityHelper mobility;
    mobility.SetPositionAllocator(
        "ns3::RandomRectanglePositionAllocator",
        "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=" +
                         std::to_string(g_areaWidth) + "]"),
        "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=" +
                         std::to_string(g_areaHeight) + "]"));
    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed",    StringValue("ns3::UniformRandomVariable[Min=1.0|Max=" +
                               std::to_string(g_speed) + "]"),
        "Pause",   StringValue("ns3::ConstantRandomVariable[Constant=" +
                               std::to_string(g_pauseTime) + "]"),
        "PositionAllocator",
        PointerValue(CreateObject<RandomRectanglePositionAllocator>()));
    mobility.Install(g_nodes);

    // ── Routing protocol ─────────────────────────────────────────────
    InternetStackHelper internet;
    DsrMainHelper dsrMain;
    DsrHelper dsrHelper;

    if (g_protocol == "AODV")
    {
        AodvHelper aodv;
        internet.SetRoutingHelper(aodv);
        internet.Install(g_nodes);
    }
    else if (g_protocol == "DSDV")
    {
        DsdvHelper dsdv;
        internet.SetRoutingHelper(dsdv);
        internet.Install(g_nodes);
    }
    else if (g_protocol == "OLSR")
    {
        OlsrHelper olsr;
        internet.SetRoutingHelper(olsr);
        internet.Install(g_nodes);
    }
    else if (g_protocol == "DSR")
    {
        internet.Install(g_nodes);
        dsrMain.Install(dsrHelper, g_nodes);
    }
    else
    {
        std::cerr << "[ManetSim] Unknown protocol: " << g_protocol
                  << ". Defaulting to AODV." << std::endl;
        AodvHelper aodv;
        internet.SetRoutingHelper(aodv);
        internet.Install(g_nodes);
    }

    // ── IP addressing ────────────────────────────────────────────────
    Ipv4AddressHelper ipv4;
    ipv4.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer ifaces = ipv4.Assign(devices);

    // ── UDP traffic (CBR) ────────────────────────────────────────────
    uint16_t port = 9;
    uint32_t sinkCount = std::max(1u, g_numNodes / 4);

    // Install packet sink on first sinkCount nodes
    PacketSinkHelper sink("ns3::UdpSocketFactory",
                           InetSocketAddress(Ipv4Address::GetAny(), port));
    ApplicationContainer sinkApps;
    for (uint32_t i = 0; i < sinkCount; i++)
    {
        sinkApps.Add(sink.Install(g_nodes.Get(i)));
    }
    sinkApps.Start(Seconds(1.0));
    sinkApps.Stop(Seconds(g_simTime));

    // Connect Rx callback
    for (uint32_t i = 0; i < sinkCount; i++)
    {
        sinkApps.Get(i)->TraceConnectWithoutContext(
            "Rx", MakeCallback(&RxCallback));
    }

    // Install source on remaining nodes
    double startOffset = 2.0;
    for (uint32_t i = sinkCount; i < g_numNodes; i++)
    {
        uint32_t targetSink = i % sinkCount;
        OnOffHelper onoff("ns3::UdpSocketFactory",
            InetSocketAddress(ifaces.GetAddress(targetSink), port));
        onoff.SetConstantRate(DataRate(g_dataRate), g_packetSize);
        ApplicationContainer srcApp = onoff.Install(g_nodes.Get(i));
        srcApp.Start(Seconds(startOffset));
        srcApp.Stop(Seconds(g_simTime - 1.0));
        srcApp.Get(0)->TraceConnectWithoutContext(
            "Tx", MakeCallback(&TxCallback));
        startOffset += 0.1;
        if (startOffset > g_simTime / 2)
            startOffset = 2.0;
    }

    // ── FlowMonitor ──────────────────────────────────────────────────
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    // ── NetAnim ───────────────────────────────────────────────────────
    AnimationInterface anim(g_outputDir + "/manet-animation.xml");
    anim.SetMaxPktsPerTraceFile(500000);
    for (uint32_t i = 0; i < g_numNodes; i++)
    {
        std::string label = g_protocol + "-" + std::to_string(i);
        anim.UpdateNodeDescription(g_nodes.Get(i), label);
        anim.UpdateNodeColor(g_nodes.Get(i), 0, 102, 204);
    }

    // ── PCAP traces ───────────────────────────────────────────────────
    wifiPhy.EnablePcapAll(g_outputDir + "/manet", false);

    // ── Schedule monitoring ───────────────────────────────────────────
    Simulator::Schedule(Seconds(0.0), &LogBattery);
    Simulator::Schedule(Seconds(0.0), &LogMobility);
    Simulator::Schedule(Seconds(1.0), &LogThroughput);

    // ── Run ───────────────────────────────────────────────────────────
    Simulator::Stop(Seconds(g_simTime));
    Simulator::Run();

    // ── FlowMonitor stats ─────────────────────────────────────────────
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier =
        DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats();

    std::ofstream flowCsv(g_outputDir + "/flowstats.csv");
    flowCsv << "FlowID,Protocol,SrcPort,DstPort,TxPackets,RxPackets,"
               "LostPackets,Throughput_kbps,MeanDelay_ms,MeanJitter_ms\n";

    for (auto &kv : stats)
    {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(kv.first);
        double tp = 0, delay = 0, jitter = 0;
        if (kv.second.rxPackets > 0)
        {
            tp    = kv.second.rxBytes * 8.0 /
                    (kv.second.timeLastRxPacket.GetSeconds() -
                     kv.second.timeFirstTxPacket.GetSeconds()) / 1000.0;
            delay  = kv.second.delaySum.GetMilliSeconds() /
                     kv.second.rxPackets;
            jitter = kv.second.jitterSum.GetMilliSeconds() /
                     kv.second.rxPackets;
        }
        flowCsv << kv.first << ","
                << (int)t.protocol << ","
                << t.sourcePort << ","
                << t.destinationPort << ","
                << kv.second.txPackets << ","
                << kv.second.rxPackets << ","
                << kv.second.lostPackets << ","
                << tp << "," << delay << "," << jitter << "\n";
    }
    flowCsv.close();

    // ── Summary stats ─────────────────────────────────────────────────
    double totalEnergy = 0.0;
    uint32_t deadNodes = 0;
    for (uint32_t i = 0; i < g_energySources.GetN(); i++)
    {
        Ptr<BasicEnergySource> src =
            DynamicCast<BasicEnergySource>(g_energySources.Get(i));
        if (src)
        {
            double rem = src->GetRemainingEnergy();
            totalEnergy += rem;
            if (rem < 0.001) deadNodes++;
        }
    }

    double overallPDR = (g_txPackets > 0)
                        ? (100.0 * g_rxPackets / g_txPackets) : 0.0;

    std::ofstream sumCsv(g_outputDir + "/summary.csv");
    sumCsv << "Protocol,NumNodes,SimTime,TxPackets,RxPackets,PDR,"
              "TotalEnergyRemaining,DeadNodes\n";
    sumCsv << g_protocol << "," << g_numNodes << "," << g_simTime << ","
           << g_txPackets << "," << g_rxPackets << "," << overallPDR << ","
           << totalEnergy << "," << deadNodes << "\n";
    sumCsv.close();

    std::cout << "[ManetSim] Done. Protocol=" << g_protocol
              << " PDR=" << overallPDR << "%"
              << " TxPkts=" << g_txPackets
              << " RxPkts=" << g_rxPackets
              << " EnergyLeft=" << totalEnergy << "J"
              << " DeadNodes=" << deadNodes << std::endl;

    g_batteryCsv.close();
    g_mobilityCsv.close();
    g_throughputCsv.close();

    Simulator::Destroy();
    return 0;
}
