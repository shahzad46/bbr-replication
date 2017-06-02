#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

oldpwd=$PWD
dir=${1:-bonus_files}
mkdir -p $dir
rm -rf $dir/*

echo "running experiment..."
python flows.py --fig-num 7 --cong bbr --time 100 --bw-net 10 --delay 10 --maxq 264 --environment mininet --flow-type iperf --dir $dir

cd $dir
echo "processing flows..."
for i in 0 1; do
    #mkdir flow$i
    #cd flow$i
    #tcptrace -T -S -R -y -A100 ../flow$i.dmp
    #cd ..
    captcp throughput -u Mbit -f 2 --stdio flow$i.dmp > captcp$i.txt
    awk '{print $1","$2 }' < captcp$i.txt > captcp-csv$i.txt
done
cd $oldpwd
python plot_throughput.py -f $dir/captcp-csv* -o $dir/bonus.png
