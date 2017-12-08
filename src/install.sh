#! /bin/bash
# Installs dependencies specific to the speedtest appliance

if [ $(id -u) -ne 0 ]; then
    echo "Please run this as root."
    exit 1
fi

PREV_DIR=$PWD

echo 'Installing iperf3...'
sudo apt remove iperf -y
sudo apt remove iperf3 -y
wget -P /tmp/ http://downloads.es.net/pub/iperf/iperf-3.1.7.tar.gz
cd /tmp
tar xvf iperf-3.1.7.tar.gz
cd iperf-3.1.7
./configure
make
sudo make install
yes | sudo pip install iperf3
echo 'Success.'

cd $PREV_DIR
