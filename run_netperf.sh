oldpwd=$PWD
python flows.py --time 50 --environment vms --flow-type netperf --dir $1
cd $1
echo "tcptracing flows..."
for i in 0 1 2 3 4; do
    mkdir flow$i
    cd flow$i
    tcptrace -T -S -R -y -A100 ../flow$i.dmp
    cd ..
    captcp throughput -u Mbit -f 1 --stdio flow$i.dmp > captcp$i.txt
    awk '{print $1","$2 }' < captcp$i.txt > netperf-csv$i.txt
done
cd $oldpwd
python plot_throughput.py -f $1/netperf-csv* -o $1/netperf-throughput.png
