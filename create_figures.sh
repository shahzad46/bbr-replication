#!/bin/bash
mkdir ./figures
sudo ./figure5.sh all figures
cp ./figure5_netperf/figure5_netperf.png ./figures/
cp ./figure5_iperf/figure5_iperf.png ./figures/
cp ./figure5_mininet/figure5_mininet.png ./figures/
sudo ./figure6.sh all figures

cp ./figure6_netperf/figure6_netperf.png ./figures/
cp ./figure6_iperf/figure6_iperf.png ./figures/
cp ./figure6_mininet/figure6_mininet.png ./figures/

sudo ./bonus.sh all figures
cp ./bonus_largebuffer/bonus_largebuffer.png ./figures/
cp ./bonus_smallbuffer/bonus_smallbuffer.png ./figures/
