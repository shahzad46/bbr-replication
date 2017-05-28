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

from monitor import monitor_qlen, monitor_bbr
import termcolor as T

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
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

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

# Linux uses CUBIC-TCP by default.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="bbr")

parser.add_argument('--fig_num',
                    type=int,
                    help="Figure to replicate. Valid options are 5 or 6",
                    default=6)

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

def start_bbrmon(dst, interval_sec=0.1, outfile="bbr.txt", host=None):
    monitor = Process(target=monitor_bbr,
                      args=(dst, interval_sec, outfile, host))
    monitor.start()
    return monitor

def iperf_bbr_mon(net, i, port):
    mon = start_bbrmon("%s:%s" % (net.get('h2').IP(), port),
                 outfile= "%s/bbr%s.txt" %(args.dir, i), host=net.get('h1'))
    return mon

# Starts n iperf flows between h1 and h2, waiting the specified time between
# starting consecutive flows.
def start_n_iperfs(net, n_iperf_flows, time_btwn_flows, action=None):
    h1 = net.get('h1')
    h2 = net.get('h2')
    print "Starting iperf flows..."
    result = []
    base_port = 1234
    for i in range(n_iperf_flows):
        start_one_iperf(h1, h2, args.cong, args.time - time_btwn_flows * i,\
                base_port + i, "{}/iperf{}.txt".format(args.dir, i))
        if action:
            result.append(action(net, i, base_port + i))
        sleep(time_btwn_flows)
    return result

# Start a ping train between h1 and h2 lasting for the given time. Send the
# output to the given fname.
def start_ping(net, time, fname):
    h1 = net.get('h1')
    h2 = net.get('h2')
    command = "ping -i 0.1 -c {} {} > {}/{}".format(time*10, h2.IP(),\
            args.dir, fname)
    h1.popen(command, shell=True)

# Start a single iperf flow between h1 and h2 with the given congestion alg,
# length of time and port number. Write the output to the specified file.
def start_one_iperf(h1, h2, cong, length, port, fname):
    command = "iperf3 -s -p {} -f m -i 1 -1 ".format(port)
    server = h2.popen(command, shell=True)
    client_command = "iperf3 -c {} -f m -w 16m -i 1 -p {} -C {} -t {}".format(\
            h2.IP(), port, cong, length)
    client_command = client_command + " > {}".format(fname)
    client = h1.popen(client_command, shell=True)

def run(action):
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()

    # This dumps the topology and how nodes are interconnected through
    # links.
    dumpNodeConnections(net.hosts)
    # This performs a basic all pairs ping test.
    net.pingAll()

    if action:
        action(net)

    # Hint: The command below invokes a CLI which you can use to
    # debug.  It allows you to run arbitrary commands inside your
    # emulated hosts h1 and h2.
    # CLI(net)

    net.stop()

# Display a countdown to the user to show time remaining.
def display_countdown(nseconds):
    start_time = time()
    while True:
        sleep(5)
        now = time()
        delta = now - start_time
        if delta > nseconds:
            break
        print "%.1fs left..." % (nseconds - delta)

def figure5(net):
    """ """
    # use fair queueing with rate 10Mbits
    os.system("tc qdisc add dev s0-eth1 root handle 5:0 fq maxrate 10mbit pacing")
    h1 = net.get('h1')
    h2 = net.get('h2')
    # Start the iperf flows.
    start_ping(net, args.time, "bbr_rtt.txt")
    start_one_iperf(h1, h2, "bbr", args.time, 2222, "bbr_iperf.txt")
    print "tracking rtt for bbr flow"
    display_countdown(args.time+5)

    start_ping(net, args.time, "cubic_rtt.txt")
    start_one_iperf(h1, h2, "cubic", args.time, 2222, "cubic_iperf.txt")
    print "tracking rtt for cubic flow"
    display_countdown(args.time+5)


def figure6(net):
    """ """
    # use fair queueing with rate 100Mbits
    os.system("tc qdisc add dev s0-eth1 root handle 5:0 fq maxrate 100mbit pacing")

    # Start the iperf flows.
    n_iperf_flows = 4
    time_btwn_flows = 2
    mons = start_n_iperfs(net, n_iperf_flows, time_btwn_flows, action=iperf_bbr_mon)

    # Print time left to show user how long they have to wait.
    start_time = time()
    args.time += n_iperf_flows * time_btwn_flows + 5
    display_countdown(args.time)

    for mon in mons:
        mon.terminate()


if __name__ == "__main__":
    if args.fig_num == 5:
        run(figure5)
    elif args.fig_num == 6:
        run(figure6)
    else:
        print "Error: please enter a valid figure number: 5 or 6"
