oldpwd=$PWD
python flows.py --time 50 --environment vms --flow-type iperf --dir $1
cd $1
echo "tcptracing and plotting flows..."
for i in 0 1 2 3 4; do
    mkdir flow$i
    cd flow$i
    tcptrace -y -A100 ../flow$i.dmp
    grep -a Mbits  ../iperf$i.txt | awk '{print $3","$7 }' | awk -F '-' '{print $2}' > ../iperf-csv$i.txt
    cd ..
done
cd $oldpwd
python plot_throughput.py -f $1/iperf-csv* -o $1/iperf-throughput.png
