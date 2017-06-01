#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

time=60
bwnet=100
# For RTT 20ms
delay=10

iperf_port=5001

for qsize in 125; do
    dir=bb-q$qsize
    rm $dir/*
    python flows.py --time $time --bw-net $bwnet --delay $delay --dir $dir --bw-host 1000 --maxq $qsize

    # TODO: Ensure the input file names match the ones you use in
    # iperf_flows.py script.  Also ensure the plot file names match
    # the required naming convention when submitting your tarball.
    #python plot_tcpprobe.py -f $dir/cwnd.txt -o $dir/cwnd-iperf.png -p $iperf_port
    for i in 0 1 2 3; do
    	grep -a Mbits  $dir/iperf$i.txt | awk '{print $3","$7 }' | awk -F '-' '{print $2}' > $dir/iperf-csv$i.txt
    done
    python plot_throughput.py -f $dir/iperf-csv* -o $dir/iperf-send.png

done
