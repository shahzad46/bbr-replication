#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from numpy import std

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

from monitor import monitor_qlen, monitor_bbr, capture_packets
import termcolor as T

import json
import sys
import os
import math

parser = ArgumentParser(description="BBR Replication")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=1000)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    )

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    )

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    required=True)

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

parser.add_argument('--flow-type',
                    default="netperf")

parser.add_argument('--environment',
                    default="vms")

# Linux uses CUBIC-TCP by default.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="bbr")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bbr experiments."

    def build(self, n=2):
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        switch = self.addSwitch('s0')
        link1 = self.addLink(host1, switch)
        link2 = self.addLink(host2, switch, bw=args.bw_net,
                             delay=str(args.delay) + 'ms',
                             max_queue_size=args.maxq)
        return


def build_topology(emulator):
    def log_wrap(fn):
        def new_fn(command, *args, **kwargs):
            print command
            return fn(command, *args, **kwargs)
        return new_fn

    if emulator == 'mininet':
        topo = BBTopo()
        net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        net.start()

        # This dumps the topology and how nodes are interconnected through
        # links.
        dumpNodeConnections(net.hosts)
        # This performs a basic all pairs ping test.
        net.pingAll()

        # use fair queueing with rate 100Mbits
        # os.system("tc qdisc add dev s0-eth1 root handle 5:0 fq maxrate 100mbit pacing")

        return {
            'type': 'mininet',
            'h1': {
                'IP': net.get('h1').IP(),
                'runner': net.get('h2').popen
            },
            'h2': {
                'IP': net.get('h2').IP(),
                'runner': net.get('h2').popen
            },
            'obj': net,
            'cleanupfn': net.stop
        }
    else:
        def ssh_runner(command, *args, **kwargs):
            user = os.environ.get('SUDO_USER', os.environ['USER'])
            full_command = "ssh -i /home/{}/.ssh/id_rsa {}@{} '{} {}'".format(
                user, user, data['h2']['IP'], 'sudo bash -c',
                json.dumps(command)
            )
            print full_command
            return Popen(command, shell=True)

        data = {
            'type': 'emulator',
            'h1': {
                'IP': '10.138.0.2',
                'runner': Popen
            },
            'h2': {
                'IP': '10.138.0.3',
                'runner': ssh_runner
            },
            'obj': None
        }
        return data


# Simple wrappers around monitoring utilities.
def start_tcpprobe(outfile="cwnd.txt"):
    os.system("rmmod tcp_probe; modprobe tcp_probe full=1;")
    Popen("cat /proc/net/tcpprobe > %s/%s" % (args.dir, outfile),
          shell=True)


def stop_tcpprobe():
    Popen("killall -9 cat", shell=True).wait()


def start_qmon(iface, interval_sec=0.1, outfile="q.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor


def start_bbrmon(dst, interval_sec=0.1, outfile="bbr.txt", runner=None):
    monitor = Process(target=monitor_bbr,
                      args=(dst, interval_sec, outfile, runner))
    monitor.start()
    return monitor


def iperf_bbr_mon(net, i, port):
    mon = start_bbrmon("%s:%s" % (net['h2']['IP'], port),
                       outfile="%s/bbr%s.txt" %(args.dir, i),
                       runner=net['h1']['runner'])
    return mon


def start_capture(outfile="capture.dmp"):
    monitor = Process(target=capture_packets,
                      args=("", outfile))
    monitor.start()
    return monitor


def filter_capture(filt, infile="capture.dmp", outfile="filtered.dmp"):
    monitor = Process(target=capture_packets,
                      args=("-r {} {}".format(infile, filt), outfile))
    monitor.start()
    return monitor


def iperf_commands(index, src, dst, port, cong, duration, outdir):
    # -s: server
    # -p [port]: port
    # -f m: format in megabits
    # -i 1: measure every second
    # -1: one-off (one connection then exit)
    server = "iperf3 -s -p {} -f m -i 1 -1 ".format(port)

    # -c [ip]: remote host
    # -w 16m: window size
    # -C: congestion control
    # -t [seconds]: duration
    client = "iperf3 -c {} -f m -w 16m -i 1 -p {} -C {} -t {} > {}".format(
        dst['IP'], port, cong, duration, "{}/iperf{}.txt".format(outdir, index)
    )

    return client, server


def netperf_commands(index, src, dst, port, cong, duration, outdir):
    # -H [ip]: remote host
    # -p [port]: port of netserver
    # -l [seconds]: duration
    # -P [port]: port of data flow
    client = "netperf -H {} -p 5555 -l {} -- -P {} > {}".format(
        dst['IP'], duration, port,
        "{}/netperf{}.txt".format(outdir, index)
    )
    server = ""
    return client, server


def netperf_setup(cong):
    client = "sysctl -w net.ipv4.tcp_congestion_control={}".format(cong)
    server = "killall netserver; netserver -p 5555"
    return client, server


def start_flows(net, num_flows, time_btwn_flows, flow_type,
                flow_monitor=None):
    h1 = net['h1']
    h2 = net['h2']

    print "Starting flows..."
    flows = []
    base_port = 1234

    if flow_type == 'netperf':
        client, server = netperf_setup(args.cong)
        if client:
            client = h1['runner'](client, shell=True)
        if server:
            server = h2['runner'](server, shell=True)        
        flow_commands = netperf_commands
    else:
        flow_commands = iperf_commands

    for i in range(num_flows):
        client, server = flow_commands(i, h1, h2, base_port + i, args.cong,
                                       args.time - time_btwn_flows * i,
                                       args.dir)
        if client:
            client = h1['runner'](client, shell=True)
        if server:
            server = h2['runner'](server, shell=True)
        flow = {
            'index': i,
            'filter': 'src {} and dst {} and dst port {}'.format(h1['IP'], h2['IP'],
                                                                 base_port + i),
            'monitor': None
        }
        if flow_monitor:
            flow['monitor'] = flow_monitor(net, i, base_port + i)
        flows.append(flow)
        sleep(time_btwn_flows)
    return flows


def run(action):
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    net = build_topology(args.environment)

    if action:
        action(net)

    # Hint: The command below invokes a CLI which you can use to
    # debug.  It allows you to run arbitrary commands inside your
    # emulated hosts h1 and h2.
    # CLI(net['obj'])

    if net['obj'] is not None and net['obj']['cleanupfn']:
        net['obj']['cleanupfn']()


def figure6(net):
    """ """

    # Start packet capturing
    cap = start_capture("{}/capture.dmp".format(args.dir))

    # Start the iperf flows.
    n_iperf_flows = 5
    time_btwn_flows = 2
    flows = start_flows(net, n_iperf_flows, time_btwn_flows, args.flow_type,
                       flow_monitor=iperf_bbr_mon)

    # Print time left to show user how long they have to wait.
    start_time = time()
    args.time += n_iperf_flows * time_btwn_flows + 5
    while True:
        sleep(5)
        now = time()
        delta = now - start_time
        if delta > args.time:
            break
        print "%.1fs left..." % (args.time - delta)

    Popen("killall tcpdump", shell=True)
    cap.join()

    for flow in flows:
        if flow['filter']:
            print "Filtering flow {}...".format(flow['index'])
            filter_capture(flow['filter'],
                           "{}/capture.dmp".format(args.dir),
                           "{}/flow{}.dmp".format(args.dir, flow['index'])) 
        if flow['monitor'] is not None:
            flow['monitor'].terminate()

if __name__ == "__main__":
    run(figure6)