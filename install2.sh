#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.
uname -a
git clone git://github.com/mininet/mininet 
mininet/util/install.sh -a 
sudo apt-get install python-termcolor
sudo apt-get install python-matplotlib

wget http://downloads.es.net/pub/iperf/iperf-3.0.11.tar.gz
tar -xvf iperf-3.0.11.tar.gz
cd iperf-3.0.11
./configure
make
sudo make install
sudo ldconfig /usr/local/lib

wget http://launchpadlibrarian.net/306560390/iproute2_4.9.0-1ubuntu1_amd64.deb
sudo dpkg -i iproute2_4.9.0-1ubuntu1_amd64.deb

sudo apt-get install tcptrace
sudo apt-get install unzip
wget https://github.com/hgn/captcp/archive/master.zip
unzip master.zip
cd captcp-master
sudo make install
sudo apt-get install python-pip
pip install dpkt
