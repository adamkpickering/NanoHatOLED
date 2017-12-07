#!/bin/bash

RESULTS_FOLDER="$PWD/results/"
DATE=$(date "+%F")
LOG_TO="$RESULTS_FOLDER/$DATE.txt"
IPERF_SERVER="192.168.1.72"
LOG_TIME="10"

# check if there is a folder named 'results'; if not, create it
if [ ! -d "$RESULTS_FOLDER" ]; then
    mkdir "$RESULTS_FOLDER"
fi

# perform iperf test
DOWN_BWIDTH=$(iperf3 -c $IPERF_SERVER -R -P 4 -t $LOG_TIME | awk '$NF=="sender" && $1=="[SUM]" { print $6 }')
UP_BWIDTH=$(iperf3 -c $IPERF_SERVER -t $LOG_TIME | awk '$NF=="sender" { print $7 }')

# append results to log file
echo $(date "+%T") $DOWN_BWIDTH $UP_BWIDTH >> $LOG_TO
