python flows.py --time 50 --environment vms --flow-type netperf --dir $1
cd $1
echo "tcptracing flows..."
for i in 0 1 2 3 4; do
    mkdir flow$i
    cd flow$i
    tcptrace -T -S -R -y -A100 ../flow$i.dmp
    cd ..
done
