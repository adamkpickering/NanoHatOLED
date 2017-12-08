#! /bin/bash
# Installs dependencies specific to the speedtest appliance

if [ $(id -u) -ne 0 ]; then
    echo "Please run this as root."
    exit 1
fi

echo 'Installing iperf3...'
yes | sudo pip install iperf3
echo 'Success.'
