#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

time=10
bwnet=10
# For RTT 40ms
delay=10

iperf_port=5001

for qsize in 125; do
    dir=figure5
    rm $dir/*
    python iperf_flows.py --time $time --bw-net $bwnet --delay $delay --dir $dir --bw-host 1000 --maxq $qsize --fig_num 5
    python plot_ping.py -f $dir/bbr_rtt.txt $dir/cubic_rtt.txt -o $dir/figure5.png

done
