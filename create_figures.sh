#!/bin/bash
mkdir -p ./figures
sudo ./figure5.sh all figures
cp ./figure5_netperf/figure5_netperf.png ./figures/figure5_netperf_vms.png
cp ./figure5_iperf/figure5_iperf.png ./figures/figure5_iperf_vms.png
cp ./figure5_mininet/figure5_mininet.png ./figures/figure5_iperf_mininet.png
sudo ./figure6.sh all figures

sudo mn -c

cp ./figure6_netperf/figure6_netperf.png ./figures/figure6_netperf_vms.png
cp ./figure6_iperf/figure6_iperf.png ./figures/figure6_iperf_vms.png
cp ./figure6_mininet/figure6_mininet.png ./figures/figure6_iperf_mininet.png

sudo mn -c
sudo ./bonus.sh all figures
cp ./bonus_largebuffer/bonus_largebuffer.png ./figures/bonus_largebuffer_mininet.png
cp ./bonus_smallbuffer/bonus_smallbuffer.png ./figures/bonus_smallbuffer_mininet.png
