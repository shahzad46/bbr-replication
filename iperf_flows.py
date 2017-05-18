#!/usr/bin/python
"CS244 Spring 2015 Assignment 1: Bufferbloat"

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

from monitor import monitor_qlen
import termcolor as T

import sys
import os
import math

# TODO: Don't just read the TODO sections in this code.  Remember that
# one of the goals of this assignment is for you to learn how to use
# Mininet. :-)

parser = ArgumentParser(description="Bufferbloat tests")
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

# Linux uses CUBIC-TCP by default that doesn't have the usual sawtooth
# behaviour.  For those who are curious, invoke this script with
# --cong cubic and see what happens...
# sysctl -a | grep cong should list some interesting parameters.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="bbr")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bufferbloat experiment."

    def build(self, n=2):
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        switch = self.addSwitch('s0')
        link1 = self.addLink(host1, switch, bw=args.bw_host,
                             delay=str(args.delay) + 'ms')
        link2 = self.addLink(host2, switch, bw=args.bw_net,
                             delay=str(args.delay) + 'ms',
                             max_queue_size=args.maxq)
        return

# Simple wrappers around monitoring utilities.  You are welcome to
# contribute neatly written (using classes) monitoring scripts for
# Mininet!
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

def start_iperf(net, n_iperf_flows, time_btwn_flows):
    h1 = net.get('h1')
    h2 = net.get('h2')
    print "Starting iperf server..."
    # For those who are curious about the -w 16m parameter, it ensures
    # that the TCP flow is not receiver window limited.  If it is,
    # there is a chance that the router buffer may not get filled up.
    base_port = 1234
    for i in range(n_iperf_flows):
        command = "iperf3 -s -p {} -f m -i 0.25 -1 ".format(base_port + i)
        server = h2.popen(command, shell=True)
        client_command = "iperf3 -c {} -f m -w 16m -i 0.5 -p {} {} -t {}".format(\
                h2.IP(), base_port + i, args.cong, args.time - time_btwn_flows * i)
        client_command = client_command + " > {}/iperf{}.txt".format(args.dir, i)
        client = h1.popen(client_command, shell=True)
        sleep(time_btwn_flows)

def bufferbloat():
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

    # Start the iperf flows.

    n_iperf_flows = 4;
    time_btwn_flows = 2;
    start_iperf(net, n_iperf_flows, time_btwn_flows)

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

    # Hint: The command below invokes a CLI which you can use to
    # debug.  It allows you to run arbitrary commands inside your
    # emulated hosts h1 and h2.
    # CLI(net)

    net.stop()
    # Ensure that all processes you create within Mininet are killed.
    # Sometimes they require manual killing.
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

if __name__ == "__main__":
    bufferbloat()
