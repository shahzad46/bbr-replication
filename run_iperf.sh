oldpwd=$PWD
python flows.py --time 50 --environment vms --flow-type iperf --dir $1
cd $1
echo "tcptracing and plotting flows..."
for i in 0 1 2 3 4; do
    mkdir flow$i
    cd flow$i
    tcptrace -T -S -R -y -A100 ../flow$i.dmp
    cd ..
    grep -a Mbits  iperf$i.txt | awk '{print $3","$7 }' | awk -F '-' '{print $2}' > iperf-csv$i.txt
    captcp throughput -u Mbit -f 2 --stdio flow$i.dmp > captcp$i.txt
    awk '{print $1","$2 }' < captcp$i.txt > tcpdump-csv$i.txt

done
cd $oldpwd
python plot_throughput.py -f $1/iperf-csv* -o $1/iperf-throughput.png
python plot_throughput.py -f $1/tcpdump-csv* -o $1/iperf-tcpdump-throughput.png
