#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

sudo apt-get update
sudo apt-get build-dep linux
sudo apt-get upgrade

#download and install modified linux kernel
cd /usr/src && sudo chmod 1777 .
git clone https://github.com/sammyas/linux-stable
cd /usr/src/linux-stable
wget  https://raw.githubusercontent.com/google/bbr/master/Documentation/config.gce
mv config.gce .config
make olddefconfig
make prepare
make -j`nproc`
make -j`nproc` modules
sudo bash -c 'echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf'
sudo bash -c 'echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf'
sudo make -j`nproc` modules_install install
sudo reboot now
