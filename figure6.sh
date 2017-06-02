#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

oldpwd=$PWD
dir=${1:-figure6_files}
mkdir -p $dir
rm -rf $dir/*

echo "running experiment..."
python flows.py --fig-num 6 --cong bbr --time 51 --bw-net 100 --delay 5 --maxq 1024 --environment mininet --flow-type iperf --dir $dir

cd $dir
echo "processing flows..."
for i in 0 1 2 3 4; do
    #mkdir flow$i
    #cd flow$i
    #tcptrace -T -S -R -y -A100 ../flow$i.dmp
    #cd ..
    captcp throughput -u Mbit --stdio flow$i.dmp > captcp$i.txt
    awk "{print (\$1+$i*2-1)(\",\")(\$2) }" < captcp$i.txt > captcp-csv$i.txt
done
cd $oldpwd
python plot_throughput.py -f $dir/captcp-csv* -o $dir/figure6.png
