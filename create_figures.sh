#!/bin/bash
mkdir -p ./figures
sudo ./figure5.sh all figures
cp ./figure5_mininet/figure5_mininet.png ./figures/figure5_iperf_mininet.png
sudo ./figure6.sh all figures

sudo mn -c

cp ./figure6_mininet/figure6_mininet.png ./figures/figure6_iperf_mininet.png

sudo mn -c
