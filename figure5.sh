#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

oldpwd=$PWD
dir=${1:-figure5_files}
mkdir -p $dir
rm -rf $dir/*

echo "running experiment..."
python flows.py --fig-num 5 --time 10 --bw-net 10 --delay 40 --maxq 200 --environment mininet --flow-type iperf --dir $dir

#captcp throughput -u Mbit -f 2 --stdio $dir/flow_bbr.dmp > $dir/tput_bbr.txt
#awk '{print $1","$2 }' < $dir/tput_bbr.txt > $dir/tcpdump-bbr.csv
#captcp throughput -u Mbit -f 2 --stdio $dir/flow_cubic.dmp > $dir/tput_cubic.txt
#awk '{print $1","$2 }' < $dir/tput_cubic.txt > $dir/tput_cubic.csv
#python plot_throughput.py -f $dir/*.csv -o $dir/fig5_tput.png

python plot_ping.py -f $dir/bbr_rtt.txt $dir/cubic_rtt.txt -o $dir/figure5.png
