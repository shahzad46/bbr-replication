#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

oldpwd=$PWD
dir=${1:-figure5_files}
mkdir -p ./figure5_files
rm -rf $dir/*

echo "running experiment..."
python flows.py --fig-num 5 --time 10 --bw-net 10 --delay 10 --maxq 100 --environment mininet --flow-type iperf --dir $dir
chmod -R 0777 $dir
su $SUDO_USER -c "tshark -2 -r $dir/flow_bbr.dmp -R 'tcp.analysis.ack_rtt' -e tcp.analysis.ack_rtt -Tfields > $dir/bbr_rtt.txt"
su $SUDO_USER -c "tshark -2 -r $dir/flow_cubic.dmp -R 'tcp.analysis.ack_rtt' -e tcp.analysis.ack_rtt -Tfields > $dir/cubic_rtt.txt"

python plot_ping.py -f $dir/bbr_rtt.txt $dir/cubic_rtt.txt -o $dir/figure5.png
