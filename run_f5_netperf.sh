oldpwd=$PWD
python flows.py --time 10 --bw-net 40 --delay 40 --maxq 200 --environment vms --flow-type netperf --dir $1

echo "tcptracing and plotting flows..."

#captcp throughput -u Mbit -f 2 --stdio $1/flow_bbr.dmp > $1/tput_bbr.txt
#awk '{print $1","$2 }' < $1/tput_bbr.txt > $1/tcpdump-bbr.csv
#captcp throughput -u Mbit -f 2 --stdio $1/flow_cubic.dmp > $1/tput_cubic.txt
#awk '{print $1","$2 }' < $1/tput_cubic.txt > $1/tput_cubic.csv
#python plot_throughput.py -f $1/*.csv -o $1/fig5_tput.png

python plot_ping.py -f $1/bbr_rtt.txt $1/cubic_rtt.txt -o $1/fig5.png
